import keyring

print('This program will set up secure email credentials using keyring for the purpose of sending email notifications.')
print('Note for maximum security it is strongly adviced to adhere to the following advice.')
print()

print('1. Do not use a personal email address.')
print('2. Be conservative in sending email notifications.')
print('3. Only send email notifications on a machine that has a small (preferably 1) number of trusted users.')

email_address=input(r'What is the email address you want to use to send emails?: ')
password=input(r'What is your login password?: ')
keyring.set_password('gmail',email_address,password)