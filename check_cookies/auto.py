import pyautogui
from check_cookies.utils import logger, click_to, waiting_for, paste_text, deciscion

failed = 0
passed = 0


with open("new-133.txt", encoding='utf-8') as file:
    for line in file.readlines():
        line = line.strip()
        if line != "":
            logger.info(f"cookies: {line}")
            logger.info(f"number passed : {passed}")
            logger.info(f"number failed : {failed}")
            # if not check_exist("import.png"):
            click_to("app.png")
            # click_to("import.png")

            left, top = waiting_for("import.png")
            pyautogui.click(left, top - 50)
            paste_text(line)
            click_to("import.png")
            click_to("check_page.PNG")

            # time.sleep(1.5)
            buttons = ["cookies_alive_1.PNG", "dark_logo.PNG", "cookies_failed.PNG",
                       "cookies_failed_1.PNG", "cookies_failed_2.PNG"]
            result = deciscion(buttons)
            if result:
                x, y, btn_index = result
                if btn_index == 0 or btn_index == 1:
                    with open("old/pass.txt", "a", encoding='utf-8') as myfile:
                        myfile.write(line + '\n')
                        passed += 1
                        myfile.close()
                        logger.info("cookies passed")
                else:
                    with open("old/failed.txt", "a", encoding='utf-8') as myfile:
                        myfile.write(line + '\n')
                        failed += 1
                        myfile.close()
                        logger.info("cookies failed")
            else:
                with open("old/failed.txt", "a", encoding='utf-8') as myfile:
                    myfile.write(line + '\n')
                    failed += 1
                    myfile.close()
                    logger.info("cookies failed")
