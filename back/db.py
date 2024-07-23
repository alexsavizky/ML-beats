import mysql.connector
import re
from dotenv import load_dotenv
import os
import logging as lg


class Db:
    def __init__(self):
        # Connect to the MySQL database
        load_dotenv()
        host, user, password, database = os.getenv("host"), os.getenv("user"), os.getenv("password"), os.getenv(
            "database")
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

    # def get_user_by_id(self, id):
    #     self.cursor.execute("SELECT * FROM users")
    #     result = self.cursor.fetchall()
    #     for i in result:
    #         if id == i[0]:
    #             user = User()
    #             user.tupple_insert(i)
    #             lg.debug(user)
    #             return user
    #     return False

    # def get_user_by_email(self, email):
    #     email = email.lower()
    #     self.cursor.execute("SELECT * FROM users")
    #     result = self.cursor.fetchall()
    #     for i in result:
    #         if email == i[1]:
    #             user = User()
    #             user.tupple_insert(i)
    #             lg.debug(user)
    #             return user
    #     return False


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


db = Db()
# with Db() as db:
#     db.create_user_table()

