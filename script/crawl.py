from bs4 import BeautifulSoup
import os

out_put = "The videos.txt"

# if os.path.isfile(out_put):
#     os.remove(out_put)


page_name = "The videos _ Facebook.html"
html_doc = open(f"C:\\Users\\HOMEPC\\Downloads\\{page_name}", encoding="utf-8")
soup = BeautifulSoup(html_doc, 'html.parser')

for parent in soup.find_all(class_='n851cfcs'):
    child = parent.find(class_="bi6gxh9e")
    href = None
    view_count = None
    if child:
        href_el = child.find("a")
        href = href_el.get('href')
        views = parent.find_all(class_="bnpdmtie")
        for view in views:
            if "Views" in view.text:
                view_count = view.text
                break
        if view_count and href:
            with open(out_put, 'a') as file:
                file.write(f"{href}-{view_count}\n")
                file.close()
                print(href, view_count)
            # if "M" in view_count:
            #     view_count_float = view_count.replace("M", "").replace("Views", "")
            #     view_count_float = float(view_count_float)
            #     # if view_count_float > 1:
            #     with open(out_put, 'a') as file:
            #         file.write(f"{href}-{view_count}\n")
            #         file.close()
            #         print(href, view_count)
            # elif "K" in view_count:
            #     view_count = view_count.replace("K", "").replace("Views", "")
            #     view_count = float(view_count)
            #     if view_count > 5:
            #         print(href, view_count)
            #         with open(out_put, 'a') as file:
            #             file.write(f"{href}-{view_count}K Views \n")
            #             file.close()
