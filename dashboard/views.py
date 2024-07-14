from flask import  Flask,render_template, Blueprint,jsonify,request,send_file, redirect,url_for
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
from flaskext.mysql import MySQL #pip install flask-mysql
import pymysql
import qrcode
import os


dash=Blueprint('dashboard', __name__,template_folder='templates',static_folder='static', static_url_path='/dashboard/static')

app = Flask(__name__)

mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'db'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'mydatabase'
mysql.init_app(app)

 
@dash.route('/admin/')
def ff():
    return render_template('admin.html')

@dash.route('/admin/French.json')
def hj():
    return render_template('French.json')

@dash.route('/admin/badge/<string:jj>', methods=["GET"])
def yy(jj):
    filename_without_extension = jj.split(".")[0]
    clean_url = jj.split("&&")[0]
        # Split the URL by the '&&' delimiter
    parts = jj.split('&&')

    # Initialize the value of 'traitont' to None
    traitont_value = None

    # Loop through the parts to find the 'traitont' parameter
    for part in parts:
        if 'traitont=' in part:
            # Split the part by '=' to get the value of 'traitont'
            traitont_value = part.split('=')[1]
            break
    return render_template('badge.html', image=clean_url,traitont=traitont_value,text=filename_without_extension)

@dash.route("/admin/ajaxfile", methods=["POST", "GET"])
def ajaxfile():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if request.method == "POST":
            draw = request.form["draw"]
            start = int(request.form["start"])
            length = int(request.form["length"])
            search_value = request.form["search[value]"]

            like_string = "%" + search_value + "%"
            cursor.execute(
                "SELECT count(*) as allcount from mycard WHERE username LIKE %s OR fonction LIKE %s OR nom_entreprise LIKE %s",
                (like_string, like_string, like_string),
            )
            rs_all_count = cursor.fetchone()
            total_records = rs_all_count["allcount"]

            if search_value == "":
                cursor.execute(
                    "SELECT * FROM mycard ORDER BY id DESC LIMIT %s, %s;",
                    (start, length),
                )
            else:
                cursor.execute(
                    "SELECT * FROM mycard WHERE username LIKE %s OR fonction LIKE %s OR nom_entreprise LIKE %s ORDER BY id DESC LIMIT %s, %s;",
                    (like_string, like_string, like_string, start, length),
                )
            employee_list = cursor.fetchall()

            data = []
            for row in employee_list:
                data.append(
                    {
                        "id": row["id"],
                        "username": row["username"],
                        "image": row["image"],
                        "fonction": row["fonction"],
                        "nom_entreprise": row["nom_entreprise"],
                        "mail": row["mail"],
                        "sou_traitont": row["sou_traitont"],

                        "delete": f'<a href="javascript:void();" data-id="{row["id"]}" data-matricule="{row["matricule"]}" data-mail="{row["mail"]}" data-groupes="{row["groupe_s"]}" data-username="{row["username"]}" data-image="{row["image"]}" data-fonction="{row["fonction"]}" data-nom_entreprise="{row["nom_entreprise"]}" class="btn btn-info btn-sm editbtn">Modifier</a><a href="javascript:void();" data-id="{row["id"]}" class="btn btn-danger btn-sm deleteBtn">Supprimer</a><a href="javascript:void();" data-id="{row["id"]}" data-username="{row["username"]}" data-image="{row["image"]}"data-matricule="{row["matricule"]}" data-fonction="{row["fonction"]}" data-nom_entreprise="{row["nom_entreprise"]}" data-grouppe="{row["groupe_s"]}" data-mail="{row["mail"]}" data-traitont="{row["sou_traitont"]}" class="btn btn-success btn-sm badge">Générer un badge</a>',
                    }
                )

            response = {
                "draw": draw,
                "iTotalRecords": total_records,
                "iTotalDisplayRecords": total_records,
                "aaData": data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred"})
    finally:
        cursor.close()
        conn.close()


@dash.route("/admin/add", methods=["POST"])
def add_employee():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            username = request.form.get('username')
            cursor.execute("SELECT * FROM mycard where  username = %s;", (username))
            row = cursor.fetchone()
            if row is not None:
                data = {'status': 'false'}
                return jsonify(data)
            else:
                fonction = request.form.get('fonction')
                nom_entreprise = request.form.get('nom_entreprise')
                groupe_s = request.form.get('groupe_s')
                selectedValue = request.form.get('selectedValue')
                mail = request.form.get('mail')
                matricule = request.form.get('matricule')

                if 'file' not in request.files:
                    return 'No file part'
                file = request.files['file']
                if file.filename == '':
                    return 'No selected file'
                # Save the file to a desired location
                file.save('dashboard/static/images/' + file.filename)
                cursor.execute("INSERT INTO mycard (username, image, fonction, nom_entreprise, groupe_s,sou_traitont,mail,matricule) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (username, file.filename, fonction, nom_entreprise, groupe_s,selectedValue,mail,matricule))
                conn.commit()
                data = {'status': 'true'}
                return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500
    finally:
        cursor.close() 
        conn.close()



@dash.route("/admin/edit/<int:id>", methods=["PUT"])
def edit_user(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'PUT':
            
            username = request.form.get('username')
            fonction = request.form.get('fonction')
            nom_entreprise = request.form.get('nom_entreprise')
            groupe_s = request.form.get('groupe_s')
            mail = request.form.get('mail')
            matricule = request.form.get('matricule')

            if 'file' not in request.files:
                return 'No file part'
            file = request.files['file']
            if file.filename == '':
                return 'No selected file'
                # Save the file to a desired location
            file.save('dashboard/static/images/' + file.filename)
            cursor.execute("UPDATE mycard SET username=%s ,fonction=%s,nom_entreprise=%s,groupe_s=%s,mail=%s,image=%s,matricule=%s WHERE id=%s;", (username,fonction,nom_entreprise,groupe_s,mail, file.filename,matricule, id))
            conn.commit()
            return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500
    finally:
        cursor.close() 
        conn.close()






@dash.route("/admin/delete/<int:id>", methods=["DELETE"])
def delete_employee(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'DELETE':
            cursor.execute("DELETE FROM mycard WHERE id=%s;", (id,))
            conn.commit()
            data = {'status': 'true'}
            return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500
    finally:
        cursor.close() 
        conn.close()

def insert_line_break(phrase):
    words = phrase.split()
    if len(words) > 4:
        index = phrase.find(words[6])
        return phrase[:index] + '\n' + phrase[index:]
    return phrase
def round_image(image, radius):
    width, height = image.size
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, width, height), fill=255)
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)
    return result
@dash.route('/admin/image/', methods=["POST"])
def add_text_to_image():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            imageuser = request.form.get('image')
            fonction = request.form.get('fonction')
            nom_departement = request.form.get('nom_entreprise')
            groupe = request.form.get('groupe')
            mail = request.form.get('mail')
            slctedValue = request.form.get('selectedValue')
            matricule = request.form.get('matricule')

            # Load the image
            image_path = os.path.join(os.getcwd(), 'dashboard/static/','rectoo.png')
            image = Image.open(image_path)

            # Add text to the image
            draw = ImageDraw.Draw(image)
              # You can also specify a font file here

            font_path = "dashboard/static/Helvetica-Bold.ttf"
            font = ImageFont.truetype(font_path, 32)
            #font = ImageFont.truetype(font_path, 32)

            draw.text((50, 360), username, font=font, fill=(35,55,141))

            fontt =ImageFont.truetype(font_path, 32)
            result = insert_line_break(fonction)
            draw.text((50, 410), result, font=fontt, fill=(35,55,141))

            fonttt =ImageFont.truetype(font_path, 32)
            draw.text((50, 530), groupe, font=fonttt, fill=(0,150,65))
            draw.text((50, 620), mail, font=fonttt, fill=(0,150,65))
            draw.text((50, 575), matricule, font=fonttt, fill=(0,150,65))

            fontttt =ImageFont.truetype(font_path, 32)
            draw.text((50, 460), nom_departement, font=fontttt, fill=(35,55,141))
            if(slctedValue=='oui'):
                tt =ImageFont.truetype(font_path, 34)
                draw.text((50, 24), 'Sous-Traitant', font=tt, fill=(35,55,141))
            else:
                image_logo = Image.open(os.path.join(os.getcwd(), 'dashboard/static/','logo_btph.jpg'))
                image_logo_resize = image_logo.resize((220, 190))  # Resize as needed
                image.paste(image_logo_resize, (560, 108))
            # Resize and paste the user image
            image_user = Image.open(os.path.join(os.getcwd(), 'dashboard/static/images/', imageuser))
            image_user_resize = image_user.resize((255, 255))  # Resize as needed
            image.paste(image_user_resize, (50, 80))

            # Generate and paste QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data('Sous Traitont :\n' + username + '\n' + fonction)  # URL or text you want to encode
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image_resized = qr_image.resize((110, 110))  # Resize as needed
            #image.paste(qr_image_resized, (980, 531))  # Position QR code on the image

            # Save the modified image
            image_path_modified = os.path.join(os.getcwd(), 'dashboard/static/images/badge/', username + '.jpg')
            image.save(image_path_modified, 'JPEG')

            # Serve the modified image
            return send_file(image_path_modified, mimetype='image/jpeg')
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred"})




if __name__ == "__main__":
    app.run(host='0.0.0.0')



