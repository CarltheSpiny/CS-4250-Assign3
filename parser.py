from bs4 import BeautifulSoup
from pymongo import MongoClient

url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"


def connectDataBase():
    DB_NAME = "web_crawler_db"
    DB_HOST = "localhost"
    DB_PORT = 21017
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client[DB_NAME]

        return db

    except:
        print ("Could not connect to the database")



def parser():
    db = connectDataBase()
    collection = db["crawled_pages"]
    professors = db["professors"]
    cursor = collection.find({})

    for document in cursor:
        html_body = document["content"]
        bs = BeautifulSoup(html_body, "html.parser")

        prof_main = bs.find_all('div', {"id":"main"})[0]
        prof_details = prof_main.find_all("p")
        prof_names = prof_main.find_all("h2")
        links = prof_main.find_all("a")

        names = []
        titles = []
        office = []
        email = []
        website = []

        # Find names
        for name in prof_names:
            names.append(name.text.strip())

        for link in links:
            parsed_link = link.get("href")
            if ("mailto:" in parsed_link):
                email.append(parsed_link)
            else:
                website.append(parsed_link)

        for tag in prof_details:
            contents_list = tag.contents
            index_of_title = -1
            index_of_office = -1

            for index, text in enumerate(contents_list):
                if("Title" in text.text):
                    index_of_title = index + 1
                if ("Office" in text.text):
                    index_of_office = index + 1


                if(index ==  index_of_title):
                    text_out = text.text.strip().replace(":", " ").replace("\n", "")
                    titles.append(text_out)
                if (index == index_of_office):
                    text_out = text.text.strip().replace(":", " ").replace("\n", "")
                    office.append(text_out)

        print()
        for index, name in enumerate(names):
            print("Name: " + name + " | Title: " + titles[index] +  " | Office: " + office[index] + " | Email: "
                  + email[index] + " | Website: " + website[index])
            entry = {
                "name": name,
                "title": titles[index],
                "office": office[index],
                "email": email[index],
                "website": website[index]
            }
            professors.insert_one(entry)
            print("Entry stored in collection")





if __name__ == '__main__':
    parser()