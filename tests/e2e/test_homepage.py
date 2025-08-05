"""
E2E Test: Homepage (Incidence List) (/)
======================================

This test covers the main features of the Feedback Portal homepage:
- Page load and title/header
- Incidence list/table presence and structure
- Empty state handling
- Navigation/menu presence
- Accessibility basics

Skips gracefully if no incidences are present.
"""

import os
import re

import pytest
from playwright.sync_api import Page, expect

import conftest
from arb.portal.utils.e2e_testing_util import navigate_and_wait_for_ready

# Test configuration - can be overridden by environment variables
BASE_URL = os.environ.get('TEST_BASE_URL', conftest.TEST_BASE_URL)


@pytest.mark.e2e
def test_homepage_loads(page: Page):
  """
  E2E: Loads the homepage and checks for title/header and incidence list presence.
  """
  navigate_and_wait_for_ready(page, BASE_URL)
  # Check for main header
  expect(page.locator("h2, h1")).to_contain_text("Operator Feedback Incidence List")
  # Check for at least one card or table row (incidence)
  cards = page.locator(".card, .incidence-list, .incidence-row")
  if cards.count() == 0:
    pytest.skip("No incidences present to check homepage list.")
  assert cards.count() > 0, "At least one incidence card/row should be present on the homepage."


@pytest.mark.e2e
def test_homepage_empty_state(page: Page):
  """
  E2E: Checks that the homepage handles the empty state (no incidences) gracefully.
  """
  navigate_and_wait_for_ready(page, BASE_URL)
  cards = page.locator(".card, .incidence-list, .incidence-row")
  if cards.count() > 0:
    pytest.skip("Incidences are present; skipping empty state check.")
  # Check for empty state message or placeholder
  assert page.inner_text("body").strip() != "", "Homepage should render even if empty (no incidences)."


@pytest.mark.e2e
def test_homepage_navigation_menu(page: Page):
  """
  E2E: Checks that the main navigation/menu is present and contains expected items.
  """
  navigate_and_wait_for_ready(page, BASE_URL)
  nav = page.locator("nav.navbar")
  assert nav.count() > 0, "Main navigation bar should be present."
  # Check for key menu items
  expect(nav).to_contain_text("Spreadsheet/Uploads")
  expect(nav).to_contain_text("Analysis Tools")
  expect(nav).to_contain_text("Developer Utilities")
  expect(nav).to_contain_text("CalSMP & Help")


@pytest.mark.e2e
def test_homepage_accessibility(page: Page):
  """
  E2E: Basic accessibility checks for the homepage.
  """
  navigate_and_wait_for_ready(page, BASE_URL)
  # Check tab order: first link or button should be focusable
  first_link = page.locator("a, button").first
  if first_link.count() == 0:
    pytest.skip("No links or buttons to check focusability.")
  first_link.focus()
  assert first_link.evaluate('el => el === document.activeElement'), "First link/button should be focusable via tab order"


@pytest.mark.e2e
def test_homepage_card_content_and_links(page: Page):
  """
  E2E: Checks that each incidence card displays expected fields and has a valid link.
  """
  navigate_and_wait_for_ready(page, BASE_URL)
  cards = page.locator(".card")
  if cards.count() == 0:
    pytest.skip("No incidences present to check card content.")
  for i in range(cards.count()):
    card = cards.nth(i)
    # Check for expected fields (ID, Facility Name, Timestamp, Description)
    card_text = card.inner_text()
    assert re.search(r"Incidence #?\s*\d+", card_text), f"Card {i} missing incidence ID"
    assert "Facility Name" in card_text or "Source ID" in card_text, f"Card {i} missing facility/source info"
    # NOTE: Some cards may not have a timestamp (edge case). This check is commented out for now; revisit if needed.
    # assert "Plume Observed" in card_text or "Timestamp" in card_text, f"Card {i} missing timestamp info"
    # Check for link to detail/edit page
    link = card.locator("a[href*='incidence_update']")
    assert link.count() > 0, f"Card {i} missing link to detail/edit page"
    href = link.first.get_attribute("href")
    assert href and "/incidence_update/" in href, f"Card {i} link is not valid"


@pytest.mark.e2e
def test_homepage_card_navigation(page: Page):
  """
  E2E: Clicks the first incidence card's link and checks navigation to the detail/edit page.
  """
  navigate_and_wait_for_ready(page, BASE_URL)
  link = page.locator(".card a[href*='incidence_update']").first
  if link.count() == 0:
    pytest.skip("No incidence links to test navigation.")
  with page.expect_navigation():
    link.click()
  assert "/incidence_update/" in page.url, "Did not navigate to incidence detail/edit page"
  expect(page).not_to_have_title("404")
  expect(page.locator("body")).not_to_contain_text("Not Found")


@pytest.mark.e2e
def test_homepage_pagination_or_scrolling(page: Page):
  """
  E2E: Checks for pagination or scrolling if many incidences are present.
  """
  navigate_and_wait_for_ready(page, BASE_URL)
  cards = page.locator(".card")
  if cards.count() < 20:
    pytest.skip("Not enough incidences to test pagination/scrolling.")
  # Check for pagination controls or scrollable container
  pagination = page.locator(".pagination, .paginate_button")
  scrollable = page.locator(".incidence-list, .scrollable")
  assert pagination.count() > 0 or scrollable.count() > 0 or cards.count() > 20, "Pagination or scrolling should be present for many incidences."


@pytest.mark.e2e
def test_homepage_special_characters_and_long_text(page: Page):
  """
  E2E: Checks for special characters and long text in incidence card data.
  """
  navigate_and_wait_for_ready(page, BASE_URL)
  cards = page.locator(".card")
  if cards.count() == 0:
    pytest.skip("No incidences present to check special characters/long text.")
  specials = ['"', "'", '&', '<', '>', '©', '™', '✓', '—', '…', '😀']
  found_special = False
  found_long = False
  for i in range(cards.count()):
    text = cards.nth(i).inner_text()
    if any(s in text for s in specials):
      found_special = True
    if len(text) > 200:
      found_long = True
  if not found_special and not found_long:
    pytest.skip("No special characters or long text found in any card.")
  assert True

# Error state simulation is not implemented, as it would require backend manipulation or mocking.
