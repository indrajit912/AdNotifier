#!python3.8
# A class for email message
#
# Author: Indrajit Ghosh
#
# Date: Aug 28, 2022
#

from pathlib import Path
import smtplib

from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate, COMMASPACE
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email import encoders
import mimetypes


class EmailMessage(MIMEMultipart):
    """
    A class representing an email message

    Author: Indrajit Ghosh

    Date: Aug 28, 2022

    Parameters:
    -----------
        `sender_email_id`: `str`
        `to`: `str`
        `subject`: `str`
        `email_plain_text`: `str`; (This is the email body)
        `email_html_text` : `str`; (If you want to add some html text use this)
        `cc`: `str` / [`str`, `str`, ..., `str`]; (Carbon Copy)
        `bcc`: `str` / [`str`, `str`, ..., `str`]; (Blind Carbon Copy)
        `attachments` : `str` / [`str`, `str`, ..., `str`]; (Attachments)

    Returns:
    --------
        `MIMEMultipart` object (An Email Message)
    """

    def __init__(
        self,
        sender_email_id:str,
        to,
        subject:str=None,
        email_plain_text:str=None,
        email_html_text:str=None,
        cc=None,
        bcc=None,
        attachments=None
    ):

        cc = [] if cc is None else cc
        bcc = [] if bcc is None else bcc
        attachments = [] if attachments is None else attachments
        attachments = [attachments] if isinstance(attachments, str) else attachments

        if not isinstance(cc, list):
            cc = [cc]
        if not isinstance(bcc, list):
            bcc = [bcc]

        # Attributes
        self.sender = sender_email_id
        self.to = [to] if isinstance(to, str) else to
        self.cc = cc
        self.bcc = bcc
        self.recipients = self.to + self.cc + self.bcc
        self.subject = subject
        self.plain_msg = email_plain_text
        self.html_msg = email_html_text
        self.attachments = attachments

        MIMEMultipart.__init__(self)

        # Structure email
        if sender_email_id in ["ma19d002@smail.iitm.ac.in", "indrajitghosh912@outlook.com"]:
            self['From'] = formataddr(("Indrajit Ghosh (SRF, SMU, ISIBc)", sender_email_id))
        elif sender_email_id == "indrajitsbot@gmail.com":
            self['From'] = formataddr(("Indrajit's Bot", sender_email_id))
        else:
            self['From'] = self.sender

        self['To'] = COMMASPACE.join(self.to)
        self['Cc'] = COMMASPACE.join(self.cc) if cc != [] else ''
        self['Bcc'] = COMMASPACE.join(self.bcc) if bcc != [] else ''
        self['Date'] = formatdate(localtime=True)
        self['Subject'] = subject

        # Attaching email text
        if self.plain_msg is not None:
            self.attach(MIMEText(self.plain_msg, 'plain'))
        if self.html_msg is not None:
            self.attach(MIMEText(self.html_msg, 'html'))

        # Adding attachments
        self.add_attachments()
        
    
    def add_attachments(self):
        
        for attached_file in self.attachments:

            attached_file = Path(attached_file)

            my_mimetype, encoding = mimetypes.guess_type(attached_file)

            if my_mimetype is None or encoding is not None:
                my_mimetype = 'application/octet-stream' 


            main_type, sub_type = my_mimetype.split('/', 1)# split only at the first '/'

            #this part is used to tell how the file should be read and stored (r, or rb, etc.)
            if main_type == 'text':
                print("text attached")
                temp = open(attached_file, 'r')  # 'rb' will send this error: 'bytes' object has no attribute 'encode'
                attachment = MIMEText(temp.read(), _subtype=sub_type)
                temp.close()

            elif main_type == 'image':
                print("image attached")
                temp = open(attached_file, 'rb')
                attachment = MIMEImage(temp.read(), _subtype=sub_type)
                temp.close()

            elif main_type == 'audio':
                print("audio attached")
                temp = open(attached_file, 'rb')
                attachment = MIMEAudio(temp.read(), _subtype=sub_type)
                temp.close()            

            elif main_type == 'application' and sub_type == 'pdf':   
                temp = open(attached_file, 'rb')
                attachment = MIMEApplication(temp.read(), _subtype=sub_type)
                temp.close()

            else:                              
                attachment = MIMEBase(main_type, sub_type)
                temp = open(attached_file, 'rb')
                attachment.set_payload(temp.read())
                encoders.encode_base64(attachment)
                temp.close()

            filename = attached_file.name
            attachment.add_header('Content-Disposition', 'attachment', filename=filename) # name preview in email
            self.attach(attachment)


    def send(self, sender_email_password, server_info=None, print_success_status=True):
        # creates SMTP session
        server_name, server_port = server_info

        server = smtplib.SMTP(server_name, server_port)

        # start TLS for security
        server.starttls()

        # Authentication
        server.login(self.sender, sender_email_password)


        # sending the mail
        server.sendmail(self.sender, self.recipients, self.as_string())

        if print_success_status:
            print("\n\t The email has been sent successfully.\n")


        # terminating the session
        server.quit()




def main():
    print('A class for Email Message!\nAuthor: Indrajit Ghosh\n')


if __name__ == '__main__':
    main()