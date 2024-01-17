import base64
  

  
with open('D:/list.csv', 'rb') as text_file:
    text_content = text_file.read()
    text_content_base64 = base64.b64encode(text_content)
    print(text_content_base64.decode('utf-8'))
