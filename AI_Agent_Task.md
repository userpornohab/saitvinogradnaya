# Prompt for AI Agent: Frontend Enhancement for Guest House Website

## General Context
Project: Guest house website with occupancy tracking and cost calculation system.
Stack: FastAPI backend (**DO NOT TOUCH**), Vue.js frontend (primary work area).
Current state: Backend ~90% complete, frontend ~50% complete.

### Global Requirements
- **Do not break existing business logic** or API interactions.
- **Do not modify** the design of already completed room blocks and the occupancy calendar (they are final).
- Ensure a **unified visual style** for:
  - Main page (landing)
  - Dynamic individual room page
  - Admin panel
- Ensure **full responsiveness** for mobile devices and tablets (mobile-first approach).
- Select a **single, pleasant, readable font** (e.g., Inter, Roboto, Nunito Sans, or a similar modern sans-serif). Font size must be adaptive (`clamp()` or rem).
- Reference design inspiration from: [Sutochno.ru](https://sutochno.ru/), [Airbnb](https://ru.airbnb.com/), but do not copy blindly.

---

## 1. Main Page (Landing)

Assemble/supplement blocks in the specified order. Each block should be a separate component for maintainability.

### Block 1: Navigation and Hero Section
- **Navigation bar**: site logo/icon on the left. Minimal menu (possibly only an admin login button if auth is present).
- **Hero**:
  - Main background photo of the guest house (set via CSS `background`).
  - Large guest house name/title.
  - **Quick booking form** (check-in/out dates, guest count).
    - **Important**: redesign the current form to be more modern (airy fields with icons, soft shadows).
    - **Functionality**: clicking "Search" / "Check Prices" should trigger a **smooth scroll** to the Rooms block (Block 4).

### Block 2: About Us / Business Card
- Two-column layout (stacked on mobile).
  - **Left**: nice photo of the courtyard or common area.
  - **Right**: text description of the guest house, welcome message, brief philosophy.

### Block 3: Amenities / Advantages
- Grid of icons with captions (e.g., Free Wi-Fi, Parking, Transfer, Sea/Mountain View, Kitchen).
- Design: icons in a unified style (outline or duotone), concise text.

### Block 4: Rooms (!!! DO NOT CHANGE DESIGN !!!)
- **Warning**: Room card structure and styles are already complete.
- **Task**: Ensure the block is correctly integrated into the new layout, has proper spacing, and the scroll anchor from Block 1 works.
- **Data**: Loaded from the backend (existing functionality).

### Block 5: Frequently Asked Questions (FAQ)
- List of questions and answers (accordion or simple list).
- **Important**: Data must be automatically loaded from the backend (FAQ endpoint exists or will exist).

### Block 6: How to Get Here
- Interactive map (Yandex/Google/2GIS) with a pin for the house.
- Below or beside the map, three tabs/tiles:
  1. **Transfer** (service description, cost if applicable).
  2. **Public Transport** (bus numbers, stops).
  3. **By Car** (coordinates, textual driving directions).

### Block 7: Nearby Landmarks
- Beautiful horizontal scroll or grid on desktop.
- Display landmark cards: photo, name, distance or travel time.
- Examples: Waterfall, Sea, Mountains, Park.

### Block 8: Reviews
- Slider (carousel) for reviews.
- Data comes from the backend.
- Review element: Guest avatar/photo (if available), Name, Review text.
- Slider navigation (arrows/dots) must be visible and clickable on mobile devices.

### Block 9: Footer
- Contacts, social media links, copyright, privacy policy link.
- Clean column layout on desktop, stacked on mobile.

---

## 2. Individual Room Page (Dynamic)

**Do not** drastically change element placement or data loading logic. Tasks are as follows:

1. **Mobile responsiveness**: Check display of all text, gallery, and calendar on narrow screens. Ensure no horizontal scroll.
2. **Photo Viewing Modal (Critical Change)**:
   - **Current**: Carousel (arrow navigation).
   - **Required**: Implement a **grid of all photos**, similar to Sutochno.ru.
     - Clicking a photo opens a modal.
     - The modal displays **all room photos at once** in a vertical scrollable feed.
     - Close button (X).
     - **Styling**: Dark background, centered photos with margins, click-to-zoom not required but the feed must be easy to browse.

---

## 3. Admin Panel

UI/UX update required. **Do not change backend logic**.

### General Requirements
- Make the design more modern and "airy".
- Unified color scheme with the main site.
- Sidebar or top menu with sections:
  - Dashboard (Statistics)
  - Edit Rooms
  - Occupancy Calendar (manual)
  - Price Management
  - Bookings/Requests (if any)

### Navigation (Active Section Highlight)
- **Important**: When the user is on a specific section (e.g., `/admin/calendar` or "Occupancy Calendar" button is pressed), the corresponding menu button must be **visually highlighted** (different background, text color, or left border).

### Section "Statistics" (Dashboard)
1. **Charts**: Add visualizations for room occupancy / revenue. Use a lightweight library (Chart.js or similar).
2. **Period Selection**:
   - Create a convenient period selection interface (today, week, month, custom range).
   - **Integration with calendar**: Connect the period selection component with the existing **custom-built calendar** used in the booking system. Selecting dates in the calendar should update the chart/statistics (or vice versa, statistics filtered by dates selected in the calendar widget).

### Section "Edit Rooms"
- Improve the design of editing forms (input fields, photo upload).
- Layout must be convenient on tablets (since admin may work from a tablet).
- **Do not touch save logic or data structure.**

---

## 4. Technical Implementation Details

### Font Responsiveness
- Use dynamic units.
- Example font import (choose a modern one):
  ```css
  @import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap');
  body { font-family: 'Nunito Sans', sans-serif; }
  h1 { font-size: clamp(2rem, 5vw, 3.5rem); }