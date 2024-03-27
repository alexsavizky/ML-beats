import mysql.connector
import re
from dotenv import load_dotenv
import os
import logging as lg
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string


class Db:
    def __init__(self):
        # Connect to the MySQL database
        load_dotenv()
        host, user, password, database = os.getenv('HOST'), os.getenv('USER'), os.getenv('PASSWORD'), os.getenv(
            'DATABASE')

        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        lg.info('db connect great success')
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
            "type int(2) , name VARCHAR(255) , lastname VARCHAR(255))")

    def insert_user(self, user):
        user.email = user.email.lower()
        query = "INSERT INTO users (email, password,type,name,lastname) VALUES (%s, %s,%s, %s,%s)"

        # check if valid email
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, user.email):
            lg.debug('not a valid email')
            lg.debug("not great success")
            return False

        # check if there is username with this email
        self.cursor.execute("SELECT email FROM users")
        result = self.cursor.fetchall()
        for i in result:
            if i[0] == user.email:
                lg.debug(f'there is {user.email} in db')
                lg.debug("not great success")
                return False

        # insert
        self.cursor.execute(query, user.totuple())
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
        user.email = user.email.lower()
        flag = False
        self.cursor.execute("SELECT email,password FROM users")
        result = self.cursor.fetchall()
        for i in result:
            if i[0] == user.email:
                flag = True
                if i[1] == user.password:
                    lg.debug("login worked great success")
                    return True
                else:
                    lg.debug("wrong password")
                    lg.debug("not great success")
                    return False
        if not flag:
            lg.debug('there is no email like this')
            lg.debug("not great success")
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

    def change_type_of_user(self, email, type):
        email = email.lower()
        query = "UPDATE users SET type = %s WHERE email = %s"
        self.cursor.execute(query, (type, email))
        self.mydb.commit()
        return True

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

    def get_all_supply(self):
        self.cursor.execute("SELECT * FROM supply")
        result = self.cursor.fetchall()
        for row in result:
            lg.debug(row)
        return result

    def borrow_item(self, user_id, item_id, return_time, num_of_items, num_of_items_remain):
        query_borrow = "INSERT INTO borrow (id_supply, id_user,num_of_items,borrow_date,return_expacted) " \
                       "VALUES (%s, %s,%s, %s,%s)"
        query_supply = "UPDATE supply SET available_units=%s WHERE id = %s"
        # update supply table
        self.cursor.execute(query_supply, (num_of_items_remain, item_id))
        # update borrow table
        now = datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(query_borrow, (item_id, user_id, num_of_items, formatted_date_time, return_time))
        self.mydb.commit()
        lg.debug(self.cursor.rowcount, "record(s) inserted.")
        lg.debug("great success")
        return True

    def return_all_items(self, user_id):
        query_find_items = "SELECT id_borrow,num_of_items,id_supply FROM borrow WHERE id_user =%s AND return_real IS NULL"
        query_return_supply = "UPDATE supply SET available_units=available_units+%s WHERE id = %s"
        query_update_borrow = "UPDATE borrow SET return_real=%s WHERE id_borrow = %s"
        now = datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(query_find_items, [user_id])
        result = self.cursor.fetchall()
        if result:
            for i in result:
                self.cursor.execute(query_update_borrow, (formatted_date_time, i[0]))
                self.cursor.execute(query_return_supply, (i[1], i[2]))

            self.mydb.commit()
            return True
        else:
            return False

    def return_item(self, user_id, item_id, how_much_items):
        query_find_items = "SELECT id_borrow,num_of_items,borrow_date,return_expacted FROM borrow WHERE id_user =%s" \
                           " AND id_supply = %s AND return_real IS NULL"
        query_update_borrow = "UPDATE borrow SET return_real=%s ,num_of_items =%s WHERE  id_borrow = %s"
        query_update_supply = "UPDATE supply SET available_units=available_units+%s WHERE  id = %s"
        query_add_remain_borrow = "INSERT INTO borrow (id_supply, id_user,num_of_items,borrow_date,return_expacted) " \
                                  "VALUES (%s, %s,%s, %s,%s)"
        query_update_borrow_return_all = "UPDATE borrow SET return_real=%s WHERE id_borrow = %s"
        now = datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(query_find_items, (user_id, item_id))
        result = self.cursor.fetchall()
        remain_to_return = int(result[0][1]) - int(how_much_items)
        # update supply table
        self.cursor.execute(query_update_supply, (how_much_items, item_id))
        if remain_to_return == 0:
            self.cursor.execute(query_update_borrow_return_all, (formatted_date_time, result[0][0]))
        else:
            self.cursor.execute(query_update_borrow, (formatted_date_time, how_much_items, result[0][0]))
            self.cursor.execute(query_add_remain_borrow,
                                (item_id, user_id, remain_to_return, result[0][2], result[0][3]))
        # result = (id_borrow,num_of_items)
        self.mydb.commit()
        return True

    def get_all_my_borrows(self, user_id):
        query = "SELECT * FROM borrow WHERE id_user = %s"
        self.cursor.execute(query, [user_id])
        return self.cursor.fetchall()

    def get_items_dosent_return(self, user_id):
        query = "SELECT * FROM borrow WHERE id_user = %s AND return_real IS NULL"
        self.cursor.execute(query, [user_id])
        return self.cursor.fetchall()

    def add_item_to_supply(self, item_name, units, item_type,description):
        query = "INSERT INTO supply (name,all_units,available_units,type,description) VALUES (%s,%s,%s,%s,%s)"
        query_id = "SELECT id FROM supply WHERE name = %s"
        self.cursor.execute(query, (item_name, units, units, item_type,description))
        self.mydb.commit()
        self.cursor.execute(query_id, [item_name])
        return self.cursor.fetchall()

    def add_units_to_supply(self, item_id, add_units):
        query = "UPDATE supply SET all_units =all_units + %s , available_units=available_units+%s WHERE id = %s"
        self.cursor.execute(query, (add_units, add_units, item_id))
        self.mydb.commit()
        return True

    def generate_temp_password(self, user_mail):
        query = 'UPDATE users SET password = %s WHERE email = %s'
        # new password 16 chars
        characters = string.ascii_letters + string.digits
        new_password = '' + ''.join(random.choice(characters) for _ in range(16))
        self.send_mail(new_password,user_mail)
        self.cursor.execute(query, (new_password, user_mail))
        self.mydb.commit()
        return True


    def get_all_borrows(self):
        query = "SELECT id_supply, id_user, num_of_items FROM borrow"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def send_mail(self,new_password,user_mail):
        load_dotenv()
        smtp_server, smtp_port, smtp_username, smtp_password = os.getenv('smtp_server'), os.getenv('smtp_port'),\
            os.getenv('smtp_username'), os.getenv('smtp_password')

        # Set up the email message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = user_mail
        msg['Subject'] = "Supply Solutions"
        body = "Greetings my sweet, it seems your brain went on a vacation and forgot your special word combo.\n" \
               " Fret not, for we have donned our wizard hats and concocted a brand new one for you! \n" \
               "Behold, your shiny new password has arrived, like a knight in shining armor to rescue you from the " \
               "land of forgotten passwords.\n your new password :" + new_password + \
               '\n #ISwearIWillNeverForgetMyPasswordAgain #IGiveYouPermissionToMurderMyEntireFamilyIfIForgetAgain'
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, msg['To'], msg.as_string())


    def plot_borrow(self):
        query = 'SELECT borrow_date, num_of_items From borrow'
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        borrow_data= [i[0] for i in data]
        num_of_items=[i[1] for i in data]
        return borrow_data,num_of_items

    def report_problem_item(self,user_id,id_item,des,units):
        self.return_item(user_id,id_item,units)
        query_prob = 'INSERT INTO problems(item_id,description,units) VALUES (%s,%s,%s)'
        query_supply = "UPDATE supply SET available_units=available_units - %s, broken_units = broken_units+ %s WHERE id = %s"
        self.cursor.execute(query_prob,(id_item,des,units))
        self.cursor.execute(query_supply, (units,units,id_item))
        self.mydb.commit()
        return True


# db = Db()
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


