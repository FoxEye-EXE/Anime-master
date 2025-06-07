from playwright.sync_api import sync_playwright
from rich import print
import re
import time
from tools.subtools.helpertools.qualty import extract_and_select_quality
from tools.subtools.helpertools.page_scaner import find_episode_link  # استيراد الدالة المنفصلة

def anime_download_prepare(new_page, context):
    try:
        # الانتظار حتى يظهر قسم المحتوى
        content_selector = ".anime-content"
        new_page.wait_for_selector(content_selector, timeout=30000)
        print(' ')
        print("[bold green]Extracting Anime Content:[/]")

        # استخراج قسم الملخص والمعلومات
        detail_selector = ".tab-content.anime-detail"
        detail_content = new_page.query_selector(detail_selector)
        if detail_content:
            print(' ')
            print("[bold cyan]=== Summary and Information ===[/]")

            # استخراج الملخص
            synopsis = detail_content.query_selector(".anime-synopsis")
            if synopsis:
                print(' ')
                print("[yellow]Synopsis:[/]")
                print(synopsis.inner_text().strip())
                print(' ')

            # استخراج المعلومات
            info = detail_content.query_selector(".anime-info")
            if info:
                print("[yellow]Information:[/]")
                info_paragraphs = info.query_selector_all("p")
                for p in info_paragraphs:
                    text = p.inner_text().strip()
                    if text:
                        print(f"  {text}")
                genres = info.query_selector(".anime-genre")
                if genres:
                    genre_items = genres.query_selector_all("li")
                    genres_text = ", ".join([item.inner_text().strip() for item in genre_items])
                    print(f"  Genres: {genres_text}")
                print(' ')

        # استخراج عدد الحلقات
        total_episodes = None
        episode_count_selector = ".episode-count"
        episode_count_element = new_page.query_selector(episode_count_selector)
        if episode_count_element:
            episode_count_text = episode_count_element.inner_text().strip()  # مثل "Episodes (50)"
            match = re.search(r'\((\d+)\)', episode_count_text)
            if match:
                total_episodes = int(match.group(1))
                print(f"[bold green]Total Episodes: {total_episodes}[/]")
            else:
                print("[red]Could not determine the total number of episodes.[/]")
                return None, None, None
        else:
            print("[red]Episode count element not found.[/]")
            return None, None, None

        # الانتظار حتى تظهر قائمة الحلقات
        episodes_selector = ".episode-wrap"
        new_page.wait_for_selector(episodes_selector, timeout=30000)

        # طلب اختيار رقم الحلقة من المستخدم
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

        # البحث عن رابط الحلقة باستخدام الدالة المنفصلة
        selected_episode_link = find_episode_link(new_page, chosen_episode, episodes_selector)
        
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

    except TimeoutError as te:
        print(f"[red]Timeout error while extracting anime content: {te}[/]")
        return None, None, None
    except Exception as e:
        print(f"[red]An unexpected error occurred: {e}[/]")
        return None, None, None