#!/opt/splunk/bin/python

import sys
import os
import re

from splunk import setupSplunkLogger
from bs4 import BeautifulSoup
import mailparser
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators

from tld import get_tld


#@Configuration(local=True)
@Configuration()
class MailParser(StreamingCommand):
    """ A wrapper for mail-parser with additional feature extractions for ML algorithms.

    ##Syntax

    .. code-block::
       mailparser [messagefield=<field>] [all_headers=<bool>] [adv_attrs=<string>] [true_label=<1|true|True|T|yes|Yes|Y>]

    ##Description

    A wrapper for for the python library mail-parser (https://github.com/SpamScope/mail-parser) 
    to parse a RFC5302 compliant email in Splunk as well as extract other features from an email
    in order to feed to a ML algorithm. Defualt settings: all options turned on, true/false 
    values returned as 0/1, and message in the `_raw` field.

    ##Example

    .. code-block::
        * | mailparser
    """

    messagefield = Option(
        default=None,
        doc='''
        **Syntax:** **textfield=***<fieldname>*
        **Description:** The field containing the entire email, normally this is `_raw` which is the default if not set.''',
        validate=validators.Fieldname())

    all_headers = Option(
        default=True,
        doc='''
        **Syntax:** **all_headers=***<bool>*
        **Description:** If false, returns only basic header information: To, From, Subject, Date. If true, all header information is parsed.''',
        validate=validators.Boolean())

    adv_attrs = Option(
        default=True,
        doc='''
        **Syntax:** **adv_attrs=***<bool>*
        **Description:** If true, extracts features such as `from_tld`, `body_len`, `has_masq_link`, etc. ''',
        validate=validators.Boolean())

    true_label = Option(
        default=1,
        doc='''
        **Syntax:** **true_label=***1|true|True|T|yes|Yes|Y*
        **Description:** String value, determines how true and false values will appear with default being 1 for True and 0 for False. ''',
        )

    
    @staticmethod
    def collectNameEmail(mail, attr):
        name = []
        email = []
        cim = []
        if getattr(mail, attr):
            for i in getattr(mail, attr):
                if len(i) > 1:
                    name.append(i[0])
                    email.append(i[1])
                    cim.append(i[1])
                else:
                    name.append('')
                    email.append(i[1])
                    cim.append(i[1])
            return name, email, cim
        else:
            return None, None, None

    @staticmethod
    def tryGetKeyValue(d, key, return_value=''):
        """
        Attempts to return value of key from dictionary
        """
        try:
            return d[key]
        except:
            return return_value
        
    def stream(self, records):
        if not self.messagefield:
            self.messagefield = '_raw'
        if self.true_label == 1:
            true = 1
            false = 0
        elif self.true_label == 'true':
            true = 'true'
            false = 'false'
        elif self.true_label == 'True':
            true = 'True'
            false = 'False'
        elif self.true_label == 'T':
            true = 'T'
            false = 'F'
        elif self.true_label == 'yes':
            true = 'yes'
            false = 'no'
        elif self.true_label == 'Yes':
            true = 'Yes'
            false = 'No'
        elif self.true_label == 'Y':
            true = 'Y'
            false = 'N'
        for record in records:
            mail = mailparser.parse_from_string(record[self.messagefield])
            ## Default parsing
            record['subject'] = mail.subject
            # Recipient
            (record['to_name'], record['to_email'], record['recipient']) = \
                self.collectNameEmail(mail, 'to')
            # Sender
            (record['from_name'], record['from_email'], record['src_user']) = \
                self.collectNameEmail(mail, '_from')
            # Reply-to
            (record['reply-to_name'], record['reply-to_email'], record['return_addr']) = \
                self.collectNameEmail(mail, 'reply_to')
            record['body'] = mail.body
            body_parts = mail.text_plain
            if len(body_parts) > 1:
                record['body_text_plain'] = body_parts[0]
                record['body_text_html'] = body_parts[1]
            else:
                record['body_text_plain'] = record['body']
            if mail.has_defects:
                record['has_defects'] = true
            else:
                record['has_defects'] = false
            # Attachments
            if mail.attachments:
                record['has_attachment'] = true
                record['num_attachment'] = len(mail.attachments)
                record['attachment_filename'] = []
                record['attachment_content_type'] = []
                record['attachment_payload'] = []
                for attach in mail.attachments:
                    record['attachment_payload'].append(attach['payload'])
                    if attach['filename']: 
                        record['attachment_filename'].append(attach['filename'])
                    else:
                        record['attachment_filename'].append('')
                    record['attachment_content_type'].append(attach['mail_content_type'])
            else:
                record['has_attachment'] = false
                record['num_attachment'] = 0
                record['attachment_payload'] = ''
                record['attachment_filename'] = ''
                record['attachment_content_type'] = ''
            ## Additional Header Parsing
            if self.all_headers:
                for k,v in mail.headers.items():
                    record[k] = v
            ## Advanced Attributes
            if self.adv_attrs:
                if 'from_email' in record and record['from_email'] is not None: 
                    match = re.findall(r'[^@]+@(.*)',record['from_email'][0])
                    if match:
                        url = re.sub(r'\.$','',match[0])
                        tld = get_tld(
                            url,
                            fix_protocol=True,
                            fail_silently=True
                        )
                        if tld:
                            record['from_tld'] = tld
                record['subject_len'] = len(record['subject'])
                if re.search(
                    self.tryGetKeyValue(record, 'Return_Path'),
                    self.tryGetKeyValue(record, 'From')
                ):
                    record['return_path_match_from'] = true
                else:
                    record['return_path_match_from'] = false
                if len(body_parts) > 1:
                    soup_html = BeautifulSoup(record['body_text_html'],'lxml')
                    record['link'] = soup_html.find_all('a')
                    record['num_link'] = len(record['link'])
                    record['num_uniq_link'] = len(set(record['link']))
                    if record['num_link'] > record['num_uniq_link']:
                        record['has_repeat_link'] = true
                    else:
                        record['has_repeat_link'] = false
                    link = []
                    record['masq_link'] = []
                    record['masq_link_tld'] = []
                    record['num_email_link'] = 0
                    for l in record['link']:
                        link_text = l.get_text().rstrip('\n')
                        a_link = l.get('href')
                        link.append(a_link)
                        if 'unsubscribe' in link_text.lower():
                            record['has_unsubscribe_link'] = true
                        if isinstance(a_link, str):
                            if re.search('mailto:',a_link):
                                record['num_email_link'] += 1
                        if a_link != link_text and \
                            'http' in link_text.lower() and \
                            not 'alt="http' in link_text.lower():
                                record['masq_link'].append(link)
                                record['masq_link_tld'].append(
                                    get_tld(
                                        a_link,
                                        fix_protocol=True, 
                                        fail_silently=True
                                    )
                                )
                    if 'has_unsubscribe_link' not in record: 
                        record['has_unsubscribe_link'] = false
                    if len(record['masq_link']) > 0:
                        record['has_masq_link'] = true
                        record['num_masq_link'] = len(record['masq_link'])
                    else:    
                        record['has_masq_link'] = false
                        record['num_masq_link'] = 0
                record['mail_text'] = record['subject'] + ' ' + record['body_text_plain']
                soup_text = BeautifulSoup(record['mail_text'],'lxml')
                record['mail_text'] = soup_text.get_text()
                record['body_len'] = len(record['body'])                
                if 'content="text/html' in record['body'].lower():
                    record['has_html_content'] = true
                else:
                    record['has_html_content'] = false
                if 'script type="text/javascript' in record['body'].lower():
                    record['has_javascript'] = true
                else:
                    record['has_javascript'] = false
                if 'img src="cid:' in record['body'].lower():
                    record['has_inline_img'] = true
                else:
                    record['has_inline_img'] = false
                url_query = '((?:https?|ftp)://[^\s/$.?#]+\.[^\s>]+)'
                record['url'] = re.findall(url_query,record['mail_text'])
                if record['url']:
                    record['has_url'] = true
                    record['num_url'] = len(record['url'])
                    record['num_uniq_url'] = len(set(record['url']))
                    record['num_repeat_url'] = record['num_url'] - record['num_uniq_url']
                    record['url_len'] = []
                    record['url_tld'] = []
                    for i in record['url']:
                        record['url_len'].append(len(i))
                        record['url_tld'].append(
                            get_tld(i, fix_protocol=True, fail_silently=True)
                        )
                        record['url_uniq_tld'] = set(record['url_tld'])
                else:
                    record['url'] = ''
                    record['has_url'] = false
                    record['num_url'] = false
                    record['num_uniq_url'] = false
                    record['url_len'] = false
                    record['url_tld'] = false
                    record['url_uniq_tld'] = false
                    record['num_repeat_url'] = false
                email_query = '([\w.]+@[\w.]+\.[\w.]{2,5})'
                record['email_addr'] = re.findall(email_query,record['mail_text'])
                if record['email_addr']:
                    record['has_email_addr'] = true
                    record['num_email_addr'] = len(record['email_addr'])
                    record['num_uniq_email_addr'] = len(set(record['email_addr']))
                else:
                    record['email_addr'] = ''
                    record['has_email_addr'] = false
                    record['num_email_addr'] = false
                    record['num_uniq_email_addr'] = false
               

            yield record

dispatch(MailParser, sys.argv, sys.stdin, sys.stdout, __name__)
