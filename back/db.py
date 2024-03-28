import mysql.connector
import re
from dotenv import load_dotenv
import os
import logging as lg


class Db:
    def __init__(self):
        # Connect to the MySQL database
        load_dotenv()
        host, user, password, database = os.getenv("host"), os.getenv("user"), os.getenv("password"), os.getenv("database")

        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print('db connect great success')
        self.cursor = self.mydb.cursor()

    def __enter__(self):
        self.cursor = self.mydb.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mydb.commit()
        self.cursor.close()
        self.mydb.close()

    # Create a table named Users
    def create_user_table(self):
        self.cursor.execute(
            "CREATE TABLE Users (id INT AUTO_INCREMENT PRIMARY KEY , email VARCHAR(255) , password VARCHAR(255) , "
            "access_with VARCHAR(255), first_name VARCHAR(255) , last_name VARCHAR(255))")

    def insert_user(self, user):
        email = user[0].lower()
        query = "INSERT INTO users (email, password,access_with,first_name,last_name) VALUES (%s, %s,%s, %s,%s)"

        # check if valid email
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, email):
            print('not a valid email')
            print("not great success")
            return False

        # check if there is username with this email
        self.cursor.execute("SELECT email FROM users")
        result = self.cursor.fetchall()
        for i in result:
            if i[0] == email:
                print(f'there is {email} in db')
                print("not great success")
                return False

        # insert
        self.cursor.execute(query, user)
        self.mydb.commit()
        lg.debug(self.cursor.rowcount, "record(s) inserted.")
        lg.debug("great success")
        return True

    # Retrieve some data from the 'customers' table
    def print_user_table(self):
        self.cursor.execute("SELECT * FROM users")
        result = self.cursor.fetchall()
        for row in result:
            lg.debug(row)
        return result

    def login(self, user):
        email,password = user[0].lower(),user[1]
        flag = False
        self.cursor.execute("SELECT email,password FROM users")
        result = self.cursor.fetchall()
        for i in result:
            if i[0] == email:
                flag = True
                if i[1] == password:
                    print("login worked great success")
                    return True
                else:
                    print("wrong password")
                    print("not great success")
                    return False
        if not flag:
            print('there is no email like this')
            print("not great success")
            return False

    def get_user_by_id(self, id):
        self.cursor.execute("SELECT * FROM users")
        result = self.cursor.fetchall()
        for i in result:
            if id == i[0]:
                user = User()
                user.tupple_insert(i)
                lg.debug(user)
                return user
        return False

    def get_user_by_email(self, email):
        email = email.lower()
        self.cursor.execute("SELECT * FROM users")
        result = self.cursor.fetchall()
        for i in result:
            if email == i[1]:
                user = User()
                user.tupple_insert(i)
                lg.debug(user)
                return user
        return False


    def change_password(self, email,temp_password, new_password):
        email = email.lower()
        query = "UPDATE users SET password = %s WHERE email = %s AND password=%s"
        self.cursor.execute(query, (new_password, email,temp_password))
        self.mydb.commit()
        return True

    def update_info(self, email, name, lastname):
        email = email.lower()
        id = self.get_user_by_email(email).id
        query = "UPDATE users SET email=%s,name=%s,lastname =%s WHERE id = %s"
        self.cursor.execute(query, (email, name, lastname, id))
        self.mydb.commit()
        return True

    def get_users_types(self):
        self.cursor.execute("SELECT email,type FROM users")
        result = self.cursor.fetchall()
        return result

    def delete_user_by_email(self, email):
        email = email.lower()
        query = "DELETE FROM users WHERE email = %s"
        self.cursor.execute(query, (email))
        self.mydb.commit()
        return True

with Db() as db:
    val = db.login(('alexsavizky@gmail.com','none'))
# db.add_item_to_supply("Sketchbooks", 50, "Stationery", "Blank paper for sketching and drawing.")
# db.add_item_to_supply("Colored Pencils", 100, "Art Supplies", "Assorted colors for coloring and shading.")
# db.add_item_to_supply("Watercolor Set", 20, "Art Supplies", "A set of watercolor paints for painting.")
# db.add_item_to_supply("Acrylic Paint Set", 30, "Art Supplies", "A set of acrylic paints for painting.")
# db.add_item_to_supply("Brush Set", 50, "Art Supplies", "A collection of different brushes for painting.")
# db.add_item_to_supply("Graphite Pencils", 100, "Art Supplies", "Various grades for sketching and shading.")
# db.add_item_to_supply("Charcoal Sticks", 50, "Art Supplies", "Used for creating rich and dark drawings.")
# db.add_item_to_supply("Drawing Pens", 100, "Art Supplies", "Fine-tipped pens for detailed illustrations.")
# db.add_item_to_supply("Canvas Rolls", 20, "Art Supplies", "Large rolls of canvas for painting.")
# db.add_item_to_supply("Easels", 10, "Art Supplies", "Sturdy stands for holding canvases while painting.")
# db.add_item_to_supply("Lightboxes", 5, "Design Tools", "Used for tracing and transferring drawings.")
# db.add_item_to_supply("Pantone Color Guides", 10, "Design Tools", "Reference guides for color matching.")
# db.add_item_to_supply("X-Acto Knives", 50, "Cutting Tools", "Precise cutting and trimming of materials.")
# db.add_item_to_supply("Cutting Mats", 20, "Cutting Tools", "Self-healing mats for protecting work surfaces.")
# db.add_item_to_supply("T-Squares", 30, "Measuring Tools", "Straightedges for precise measurements.")
# db.add_item_to_supply("Rulers", 100, "Measuring Tools", "Measuring and drawing straight lines.")
# db.add_item_to_supply("Protractors", 20, "Measuring Tools", "For measuring and drawing angles.")
# db.add_item_to_supply("Scalpel Blades", 100, "Cutting Tools", "Sharp blades for precise cutting.")
# db.add_item_to_supply("Glue Guns", 10, "Adhesives", "For quick and strong adhesion.")
# db.add_item_to_supply("Spray Adhesive", 20, "Adhesives", "Even coating for mounting artwork.")
# db.add_item_to_supply("Masking Tape", 50, "Adhesives", "Temporary fixing and masking.")
# db.add_item_to_supply("Drafting Tables", 5, "Furniture", "Adjustable tables for drawing and designing.")
# db.add_item_to_supply("Studio Chairs", 20, "Furniture", "Comfortable chairs for working long hours.")
# db.add_item_to_supply("Storage Cabinets", 10, "Furniture", "Organizing and storing art supplies.")
# db.add_item_to_supply("Projectors", 5, "Design Tools", "Enlarging and projecting images.")
# db.add_item_to_supply("Markers", 100, "Art Supplies", "Assorted markers for illustration and design.")
# db.add_item_to_supply("Foam Boards", 50, "Display Materials", "Lightweight boards for mounting artwork.")
# db.add_item_to_supply("Stencils", 50, "Design Tools", "Pre-cut templates for repetitive designs.")
# db.add_item_to_supply("Adhesive Vinyl", 20, "Design Materials", "Self-adhesive vinyl for signage and decals.")
# db.add_item_to_supply("Glitter", 50, "Art Supplies", "Shimmery flakes for adding sparkle to artwork.")


