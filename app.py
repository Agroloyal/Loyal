from flask import Flask, request, redirect
import pandas as pd
import os.path
from urllib.parse import quote
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)
app.secret_key = '19971997'  # تغيير "your_secret_key" إلى مفتاح سري فعلي

gauth = GoogleAuth()
gauth.LoadCredentialsFile("credentials.json")  # تغيير "credentials.json" إلى اسم ملف المصادقة الخاص بك

if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile("credentials.json")  # تغيير "credentials.json" إلى اسم ملف المصادقة الخاص بك

drive = GoogleDrive(gauth)

def create_whatsapp_message(date, serial_number, customer_name, material_name, weight, entry_exit, notes):
    message = f'تم تسجيل بيانات جديدة:\n\n'
    message += f'التاريخ: {date}\n'
    message += f'الرقم التسلسلي: {serial_number}\n'
    message += f'اسم العميل: {customer_name}\n'
    message += f'اسم المادة: {material_name}\n'
    message += f'الوزن (بالكيلو جرام): {weight}\n'
    message += f'الدخول أو الخروج: {entry_exit}\n'
    message += f'ملاحظات: {notes}\n'
    return message

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form['date']
        serial_number = request.form['serialNumber']
        customer_name = request.form['customerName']
        material_name = request.form['materialName']
        weight = request.form['weight']
        entry_exit = request.form['entryExit']
        notes = request.form['notes']

        # Create DataFrame with form data
        df = pd.DataFrame({'Date': [date], 'Serial Number': [serial_number],
                           'Customer Name': [customer_name], 'Material Name': [material_name],
                           'Weight': [weight], 'Entry/Exit': [entry_exit], 'Notes': [notes]})

        # Export DataFrame to Excel based on entry or exit
        if entry_exit == 'entry':
            file_name = 'entry_data.xlsx'
        elif entry_exit == 'exit':
            file_name = 'exit_data.xlsx'

        if os.path.isfile(file_name):
            existing_df = pd.read_excel(file_name)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_excel(file_name, index=False)

        # Upload file to Google Drive
        file1 = drive.CreateFile({'title': file_name})
        file1.SetContentFile(file_name)
        file1.Upload()

        # Create WhatsApp message
        message = create_whatsapp_message(date, serial_number, customer_name, material_name, weight, entry_exit, notes)
        encoded_message = quote(message)  # ترميز الرسالة

        # Redirect to WhatsApp link with encoded message and your desired group link
        whatsapp_link = f'https://chat.whatsapp.com/FXPRpcsv3vxF9gvN6vQDcW/?text={encoded_message}'
        return redirect(whatsapp_link)

    return '''
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>نموذج إدخال البيانات</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .form-container {
                background-color: #fff;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                width: 80%;
                max-width: 600px;
            }

            label {
                display: block;
                margin-bottom: 5px;
            }

            input, select, textarea, button {
                width: 100%;
                padding: 10px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-sizing: border-box;
            }

            button {
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
            }

            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="form-container">
            <form method="post">
                <label for="date">التاريخ:</label>
                <input type="date" id="date" name="date" required>

                <label for="serialNumber">الرقم التسلسلي:</label>
                <input type="text" id="serialNumber" name="serialNumber" required>

                <label for="customerName">اسم العميل:</label>
                <input type="text" id="customerName" name="customerName" required>

                <label for="materialName">اسم المادة:</label>
                <input type="text" id="materialName" name="materialName" required>

                <label for="weight">الوزن (بالكيلو جرام):</label>
                <input type="number" id="weight" name="weight" min="0" required>

                <label for="entryExit">الدخول أو الخروج:</label>
                <select id="entryExit" name="entryExit" required>
                    <option value="entry">الدخول</option>
                    <option value="exit">الخروج</option>
                </select>

                <label for="notes">ملاحظات:</label>
                <textarea id="notes" name="notes" rows="4" cols="50"></textarea>

                <button type="submit">إرسال</button>
            </form>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)