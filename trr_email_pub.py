#!/usr/bin/env python
# coding: utf-8

# ## Import

# In[15]:


try:
    import bs4
    import requests
    import pandas as pd
    import time as time
    import re 
    check = time.time()

    import smtplib, ssl
    import email



    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib
    from os.path import basename
    from email.mime.application import MIMEApplication
    from email.mime.text import MIMEText
    from email.utils import COMMASPACE, formatdate 
    print("Dependencies imported correctly.")
except:
    print("Dependencies failed.")


# ## Error Logging

# In[16]:


error_msg = MIMEMultipart()


# In[17]:


def send_email(body):

    print("Error")
    
# ## Scan Webpage

try:
    def make_utf8(line):
        return bytes(line, 'utf-8').decode('utf-8', 'ignore').strip()

    print(time.time())
    result = requests.get("https://www.texasregionalradio.com/Top100.asp")
    print("Results grabbed successfully.")

    #raw = open("trrr.html","r",encoding="latin-1").read()
    soup = ""
    soup = bs4.BeautifulSoup(result.text, features="html5lib")
    print(soup)
    print("Soup scan successful.")
    
    table = soup.select("table.sample tbody")
    print("Hash soup successful.")
    print((soup.h2.text)[11:20])
    songs = []
    rows = table[0].findChildren("tr", recursive=False)
    key = rows[0].findChildren("td", recursive=False)  # extract header names

    del rows[0] # toss out header row
    del rows[100:103] # toss out ad space
except:
    error_msg['Subject'] = "ERROR: TRR scan failed."
    send_email(error_msg)


# ## Parse Webpage

# In[20]:


#rows = rows[:len(rows)-18]  # toss out "next 15" rows

try:
    for row in rows:
        song = {}
        cols = row.findChildren("td", recursive=False)
        for i in range(9):
            song[make_utf8(key[i+1].getText())] = make_utf8(cols[i+1].getText())

        # Here give special attention to cols[4] which contains nested table
        del song[make_utf8(key[4].getText())]   # remove junk
        title_artist = cols[4].select("nobr")   # extract individual pieces
        song['artist'] = make_utf8(title_artist[1].getText())
        notes = title_artist[0].select("font")
        song['affiliation'] = make_utf8(notes[0].getText())
        notes[0].decompose() # remove affiliation from tree
        if len(notes) > 1:
            song['notes'] = make_utf8(notes[1].getText())
            notes[1].decompose() # remove notes from tree

        song['title'] = make_utf8(title_artist[0].getText())
        song['title'] = song['title'][:-2]

        songs.append(song)

    record = pd.DataFrame.from_dict(songs)
    print("TRR Conversion Complete")
except:
    error_msg['Subject'] = "ERROR: TRR Conversion Failed"
    send_email(error_msg)


# In[21]:


(soup.h2.text)[11:20]


# In[22]:


date = (soup.h2.text)[11:20] #str(soup.h2.text)[11:20]
d1 = date.split("/")
d2 = [item.strip() for item in d1]
date_range = d2[0] + "-" + d2[1] + "-2020"
wkbk_name = date_range + ".xlsx"
wkbk_name


# ## Save File

# In[23]:


try:
    out_path = "~/home/data/" + str(wkbk_name)
    print(out_path)
    writer = pd.ExcelWriter(wkbk_name)
    record.to_excel(writer, (wkbk_name)[:8])
    writer.save()
    print(date_range)
    print("File Saved")
except:
    error_msg['Subject'] = "ERROR: File not saved."
    send_email(error_msg)


# ## E-mail Details

# In[24]:


try:
    msg = MIMEMultipart()
    msg['Subject'] = "Texas Regional Radio Report - " + date_range
    msg['From'] = "XXXX@gmail.com"

    '''
    ## To add multiple recipients 

    recipients = ['ToEmail@domain.com'] 
    emaillist = [elem.strip().split(',') for elem in recipients
    '''

    html = """    <html>
      <head></head>
      <header><h2>Texas Regional Radio - {}</h2></header>
      <body>
        {}
      </body>
    </html>
    """.format(date_range,record.to_html())

    table = MIMEText(html, 'html')
    msg.attach(table)

except:
    error_msg['Subject'] = "ERROR: E-mail creation failed."
    send_email(error_msg)


# ## Create Attachment

# In[25]:


try:
    trr_csv = MIMEBase('application', "octet-stream")
    trr_csv.set_payload(open(wkbk_name, "rb").read())
    encoders.encode_base64(trr_csv)
    trr_csv.add_header('Content-Disposition', 'attachment; filename="%s"' % wkbk_name)
    msg.attach(trr_csv)
except:
    error_msg['Subject'] = "ERROR: Attachment not created."
    send_email(error_msg)


# ## Send E-mail

# In[26]:


send_email(msg)


# ## Future Changes

# In[27]:


record


# ## Sources

# In[28]:


## https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development
## https://stackoverflow.com/questions/26582811/gmail-python-multiple-attachments
## https://stackoverflow.com/questions/50564407/pandas-send-email-containing-dataframe-as-a-visual-table


# In[ ]:




