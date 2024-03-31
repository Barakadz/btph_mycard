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

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'btph'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
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

    return render_template('badge.html', image=jj,text=filename_without_extension)

 

@dash.route("/admin/ajaxfile",methods=["POST","GET"])
def ajaxfile():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw'] 
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)
 
            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from mycard")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            print(totalRecords) 
 
            ## Total number of records with filtering
            likeString = "%" + searchValue +"%"
            cursor.execute("SELECT count(*) as allcount from mycard WHERE username LIKE %s OR fonction LIKE %s OR nom_entreprise LIKE %s", (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            print(totalRecordwithFilter) 
 
            ## Fetch records
            if searchValue=='':
                cursor.execute("SELECT * FROM mycard ORDER BY id desc limit %s, %s;", (row, rowperpage))
                employeelist = cursor.fetchall()
            else:        
                cursor.execute("SELECT * FROM mycard WHERE username LIKE %s OR fonction LIKE %s OR nom_entreprise LIKE %s limit %s, %s;", (likeString, likeString, likeString, row, rowperpage))
                employeelist = cursor.fetchall()
 
            data = []
            for row in employeelist:
                data.append({
                    'id': row['id'],
                    'username': row['username'],
                    'image': row['image'],
                    'fonction': row['fonction'],
                    'nom_entreprise': row['nom_entreprise'],
                    'delete': f'<a href="javascript:void();"   data-id="{row["id"]}" data-groupes="{row["groupe_s"]}"  data-username="{row["username"]}"  data-image="{row["image"]}"  data-fonction="{row["fonction"]}"  data-nom_entreprise="{row["nom_entreprise"]}"    class="btn btn-info btn-sm editbtn" >Modifier</a><a href="javascript:void();"   data-id="{row["id"]}" class="btn btn-danger btn-sm deleteBtn" >supprimer</a><a href="javascript:void();"   data-id="{row["id"]}" data-username="{row["username"]}" data-image="{row["image"]}" data-fonction="{row["fonction"]}" data-nom_entreprise="{row["nom_entreprise"]}"  data-grouppe="{row["groupe_s"]}"  class="btn btn-success btn-sm badge" >Générer un badge</a>',

                })
 
            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
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
                if 'file' not in request.files:
                    return 'No file part'
                file = request.files['file']
                if file.filename == '':
                    return 'No selected file'
                # Save the file to a desired location
                file.save('dashboard/static/images/' + file.filename)
                cursor.execute("INSERT INTO mycard (username, image, fonction, nom_entreprise, groupe_s) VALUES (%s, %s, %s, %s, %s)", (username, file.filename, fonction, nom_entreprise, groupe_s))
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
            if 'file' not in request.files:
                return 'No file part'
            file = request.files['file']
            if file.filename == '':
                return 'No selected file'
                # Save the file to a desired location
            file.save('dashboard/static/images/' + file.filename)
            cursor.execute("UPDATE mycard SET username=%s ,fonction=%s,nom_entreprise=%s,groupe_s=%s,image=%s WHERE id=%s;", (username,fonction,nom_entreprise,groupe_s, file.filename, id))
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
        index = phrase.find(words[4])
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
    if request.method == 'POST':
        username = request.form.get('username')
        imageuser = request.form.get('image')
        fonction = request.form.get('fonction')
        nom_entreprise = request.form.get('nom_entreprise')
        groupe = request.form.get('groupe')

    # Load the image
        image_path = './rectoo.jpg'
        image = Image.open(image_path)

        # Add text to the image
        draw = ImageDraw.Draw(image)
        #text = "Baraka abbes ibrahim"
        font = ImageFont.truetype("arial.ttf", 32)
 
        draw.text((60, 220), username, font=font,  fill=(0, 0, 0))

        #textt = "Ingénieur de développement \n informatique"
        fontt = ImageFont.truetype("arial.ttf", 30)
        result = insert_line_break(fonction)
        draw.text((60, 280), result, font=fontt,  fill=(0, 0, 0))


        #texttt = "A +"
        fonttt = ImageFont.truetype("arial.ttf", 30)
        draw.text((120, 428), groupe, font=fonttt,  fill=(0, 0, 0))


        #textttt = "Groupe des sociétés HASNAOUI"
        fontttt = ImageFont.truetype("arial.ttf", 30)
        draw.text((120, 500), nom_entreprise, font=fontttt,  fill=(0, 0, 0))

        image_user=Image.open('dashboard/static/images/' + imageuser )
        image_user_resize = image_user.resize((255, 255))  # Resize as needed

  
        

              
       
        jjo= image_user_resize 
 
        image.paste(jjo, (810, 120) )

        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data('Sous Traitont :\n'+username+'\n'+fonction)  # URL or text you want to encode
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image_resized = qr_image.resize((110, 110))  # Resize as needed
        image.paste(qr_image_resized, (980, 531))  # Position QR code on the image

        # Add text to the image
        draw = ImageDraw.Draw(image)

        # Serve the modified image
        img_io = io.BytesIO()
        image.save(img_io, 'JPEG')
        img_io.seek(0)
        image_bytes = img_io.getvalue()
        name=username+'.jpg'
         # Save the modified image to the uploads folder
        image_path = os.path.join('dashboard/static/images/badge/', name)
        image.save(image_path, 'JPEG')

        # Return the modified image as a downloadable attachment
        send_file(
            io.BytesIO(image_bytes),
            mimetype='image/jpeg',
             
        )
        return redirect(url_for('dashboard.yy', jj=username))
















if __name__ == "__main__":
    app.run()



