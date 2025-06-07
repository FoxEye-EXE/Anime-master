from playwright.sync_api import sync_playwright
from rich import print
import re
import time
from tools.subtools.helpertools.qualty import extract_and_select_quality
from tools.subtools.helpertools.page_scaner import scan_page



context = None
def get_one(total_episodes):
    while True:
        try:
            print(' ')
            chosen_episode = int(input(f"Enter the episode number you want to select (1 to {total_episodes}, or -1 to exit): "))
            if chosen_episode == -1:
                print("[blue]Exiting episode selection.[/]")
                return None, None, None
            if 1 <= chosen_episode <= total_episodes:
                break
            else:
                 print(f"[red]Invalid episode number. Please enter a number between 1 and {total_episodes}.[/]")
        except ValueError:
            print("[red]Please enter a valid number.[/]")
    selected_episode_link = None
    current_page = 1
        
    scan_page()

    # فتح رابط الحلقة في علامة تبويب جديدة
    episode_page = None
    if selected_episode_link:
        print(' ')
        print(f"[green]Opening Episode {chosen_episode} in a new tab: {selected_episode_link}[/]")
        episode_page = context.new_page()
        time.sleep(1)
        episode_page.goto(selected_episode_link, wait_until="domcontentloaded")
        print(f"[green]Successfully opened Episode {chosen_episode} page.[/]")
        print(' ')
    else:
        print(f"[red]Failed to find the watch link for Episode {chosen_episode}.[/]")
        return None, None, None
    # استدعاء الدالة الفرعية لاستخراج الجودات وفتح رابط التحميل
    result = extract_and_select_quality(episode_page, context, selected_episode_link)
    if result is None:
        return episode_page, None, None
    download_page, final_download_page = result
    return episode_page, download_page, final_download_page
    