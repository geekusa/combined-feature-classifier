# Mail-Parser Plus Splunk App

The intent of this app is to act as a wrapper for the python library mail-parser ([https://github.com/SpamScope/mail-parser](https://github.com/SpamScope/mail-parser)) to parse a RFC5302 compliant email in Splunk as well as extract other features from an email in order to feed to a ML algorithm. The app provides a single custom command.

Available at:
[Github](https://github.com/geekusa/combined-feature-classifier/tree/master/SPLUNK_APP_SA_MAILPARSER)

Splunk App Available at:
[https://splunkbase.splunk.com/app/4066/](https://splunkbase.splunk.com/app/4129/)

Version: 1.0

##### Author: Nathan Worsham 
Created as part of MSDS692 Data Science Practicum II at Regis University, 2018 </br>
See [associated blog](https://github.com/geekusa/combined-feature-classifier) for detailed information on the project.

## Description and Use-cases

This app provides parsing and feature extraction for RFC5302 compliant emails. Note that the attachment payload does not have to be in Splunk, just its headers for it to extract attachment information like content-type.

## How to use

### Install

Normal app installation can be followed from https://docs.splunk.com/Documentation/AddOns/released/Overview/AboutSplunkadd-ons. Essentially download app and install from Web UI or extract file in $SPLUNK\_HOME/etc/apps folder.

### Custom Commands

_mailparser_
> #### Description
> A wrapper for for the python library mail-parser (https://github.com/SpamScope/mail-parser) to parse a RFC5302 compliant email in Splunk as well as extract other features from an email in order to feed to a ML algorithm. Default settings: all options turned on, true/false values returned as 0/1, and message in the `_raw` field.
> #### Syntax
> \* | mailparser [messagefield=<field>] [all\_headers=<bool>] [adv\_attrs=<string>] [true_label=<1|true|True|T|yes|Yes|Y>]
> ##### Optional Arguments
> **messagefield** </br>
>     **Syntax:** messagefield=\<field> </br>
>     **Description:** The field containing the entire email, normally this is `_raw` which is the default if not set. </br>
>     **Usage:** Option only takes a single field</br>
>     **Default:** _raw
> 
> **all\_headers** </br>
>     **Syntax:** all\_headers=\<boo;> </br>
>     **Description:** If false, returns only basic header information: To, From, Subject, Date. If true, all header information is parsed. </br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1 </br>
>     **Default:** True
> 
> **adv\_attrs** </br>
>     **Syntax:** adv\_attrs=\<bool> </br>
>     **Description:** If true, extracts features such as `from_tld`, `body_len`, `has_masq_link`, etc. See below for complete list and description. </br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1 </br>
>     **Default:** lxml
> 
>**true\_label** </br>
>     **Syntax:** true\_label=\<1|true|True|T|yes|Yes|Y> </br>
>     **Description:** String value, determines how true and false values will appear with default being 1 for True and 0 for False.</br>
>     **Usage:** 1|true|True|T|yes|Yes|Y </br>
>     **Default:** 1

#### Extracted Features (using `adv_attrs` option)
>**from\_tld**: String - Top Level Domain of the sender </br>
>**return\_path\_match\_from**: Boolean - If `Return_Path` matches `From` </br>
>**body\_len**: Integer - Character count of the body </br>
>**subject\_len**: Integer - Character count of the subject </br>
>**link**: String - Multi-value list of HTML `<a>` tags </br>
>**num\_link**: Integer - Count of HTML `<a>` tags </br>
>**num\_uniq\_link**: Integer - Count of distinct HTML `<a>` tags </br>
>**has\_repeat\_link**: Boolean - If any `href` values from HTML `<a>` tags are repeated </br>
>**has\_unsubscribe\_link**: Boolean - If any text values from HTML `<a>` tags have the word unsubscribe within </br>
>**num\_email\_link**: Integer - Count of `href` values from HTML `<a>` tags that are `mailto:` </br>
>**masq\_link**: String - Multi-value list of `href` values (actual target) from HTML `<a>` tags where the link text purports to be a URL but the target does not match the link text (masquerading link) </br>
>**masq\_link\_tld**: String - Multi-value list of Top Level Domains of masquerading link targets </br>
>**has\_masq\_link**: Boolean - If any HTML `<a>` tags' link text purports to be a URL but the target does not match the link text (masquerading link) </br>
>**num\_masq\_link**: Integer - Count of any (includes duplicates) HTML `<a>` tags' link text purports to be a URL but the target does not match the link text (masquerading link) </br>
>**mail\_text**: String - Subject and Body text combined, usually without HTML formatting (from bs4) </br>
>**has\_html\_content**: Boolean - If content in body is set to html </br>
>**has\_javascript**: Boolean - If script type in body is set to javascript </br>
>**has\_inline\_img**: Boolean - If content in body has an inline image </br>
>**url**: String - Multi-value list of URLs from body </br>
>**has\_url**: Boolean - If URL exists in the body </br>
>**num\_url**: Integer - Count of URLs in the body </br>
>**num\_uniq\_url**: Integer - Count of distinct URLs in the body </br>
>**url\_len**: Integer - Multi-value list of length of URLs from body </br>
>**url\_tld**: String - Multi-value list (including duplicates) of Top Level Domains of URLs from body </br>
>**url\_uniq\_tld**: String - Multi-value list of distinct Top Level Domains of URLs from body </br>
>**num\_repeat\_url**: Integer - Count of repeating URLs in the body </br>
>**email\_addr**: String - Multi-value list of email addresses from body </br>
>**has\_email\_addr**: Boolean - If an email address exists in the body </br>
>**num\_email\_addr**: Integer - Count of email addresses in the body </br>
>**num\_email\_addr\_url**: Integer - Count of distinct email addresses in the body </br>




### Support
Support will be provided through Splunkbase (click on Contact Developer) or Splunk Answers or [submit an issue in Github](https://github.com/geekusa/combined-feature-classifier/issues/new). Expected responses will depend on issue and as time permits, but every attempt will be made to fix within 2 weeks. 

### Documentation
This README file constitutes the documentation for the app and will be kept up to date on [Github](https://github.com/geekusa/combined-feature-classifier/SPLUNK_APP_SA_MAILPARSER/master/README.md) as well as on the Splunkbase page.


### Release Notes
Initial Release
