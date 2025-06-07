from playwright.sync_api import sync_playwright
from rich import print
import re
import time

def find_episode_link(new_page, chosen_episode, episodes_selector):
    selected_episode_link = None
    current_page = 1
    try:
        while not selected_episode_link:
            print(f"[blue]Checking episodes on page {current_page}...[/]")
            episode_items = new_page.query_selector_all(episodes_selector)
            if not episode_items:
                print(f"[red]No episodes found on page {current_page}.[/]")
                break

            # فحص كل حلقة في الصفحة الحالية
            for episode in episode_items:
                episode_number_element = episode.query_selector(".episode-number")
                if episode_number_element:
                    episode_number_text = episode_number_element.inner_text().strip()
                    episode_number_text = episode_number_text.replace("Episode", "").strip()
                    match = re.search(r'\d+', episode_number_text)
                    if match:
                        episode_number = int(match.group(0))
                        print(f"[blue]Found episode {episode_number} on page {current_page}[/]")
                        if episode_number == chosen_episode:
                            watch_link_element = episode.query_selector("a.play")
                            if watch_link_element:
                                watch_link = watch_link_element.get_attribute("href")
                                full_watch_link = f"https://animepahe.ru{watch_link}" if watch_link.startswith("/") else watch_link
                                selected_episode_link = full_watch_link
                                print(f"[green]Episode {chosen_episode} found with link: {selected_episode_link}[/]")
                                break
                else:
                    print("[red]Episode number element not found for an episode.[/]")
                    continue

            # إذا لم يتم العثور على الحلقة، حاول التنقل للصفحة التالية
            if not selected_episode_link:
                print(f"[blue]Episode {chosen_episode} not found on page {current_page}. Looking for next page...[/]")
                new_page.wait_for_load_state("networkidle", timeout=60000)
                next_page_button = new_page.query_selector("a.page-link.next-page:not(.disabled)")
                if next_page_button:
                    print(f"[blue]Next page button found on page {current_page}. Clicking it...[/]")
                    try:
                        next_page_button.click()
                        time.sleep(2)
                        new_page.wait_for_load_state("networkidle", timeout=60000)
                        new_page.wait_for_selector(episodes_selector, timeout=30000)
                        current_page += 1
                        print(f"[green]Navigated to page {current_page}.[/]")
                    except TimeoutError as te:
                        print(f"[red]Failed to load page {current_page + 1}: {te}[/]")
                        break
                    except Exception as e:
                        print(f"[red]Failed to navigate to page {current_page + 1}: {e}[/]")
                        break
                else:
                    print(f"[red]No next page button found on page {current_page}. No more pages available.[/]")
                    break

        return selected_episode_link  # إرجاع رابط الحلقة
    except Exception as e:
        print(f"[red]Error in find_episode_link: {e}[/]")
        return None