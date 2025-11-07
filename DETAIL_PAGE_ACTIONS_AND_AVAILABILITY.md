# Book Detail Page - Actions and Availability Information

## Action Buttons

### 1. Vorbestellen (Reserve)
- **Text**: "Vorbestellen" (Reserve)
- **Type**: Link (styled as button with class `btn btn-primary`)
- **Class**: `tosic-oclc-btn-with-icon tosic-oclc-btn-reserve`
- **Action**: `javascript:__doPostBack('dnn$ctr365$MainViewGraz$UcDetailView$ucSharedCatalogueView$BtnReserve','')`
- **Purpose**: Reserve the book when not available
- **Icon**: Calendar icon
- **Availability**: Only shown if book is checked out or user wants to reserve

### 2. Medium auf die Postliste setzen (Add to Waitlist/Mail Order)
- **Text**: "Medium auf die Postliste setzen"
- **Type**: Link (styled as button with class `btn btn-primary`)
- **Class**: `tosic-oclc-btn-with-icon`
- **URL**: `/Mediensuche/Postservice`
- **Purpose**: Add book to mail order waitlist
- **Icon**: Envelope/mail icon
- **Availability**: Always shown
- **Note**: Links to separate Postservice page for mail order requests

## Exemplare (Copies) Table Structure

### Table Headers (from screenshot)
| Column | Content |
|--------|---------|
| ZWEIGSTELLE | Branch/Location |
| SIGNATUR | Call Number |
| STANDORT 2 | Section/Department |
| STATUS | Availability Status |
| VORBESTELLUNGEN | Number of Reservations |
| MEDIENGRUPPE | Media Type |
| FRIST | Due Date (if checked out) |
| BARCODE | Item Barcode |
| STANDORT 3 | Additional Location Info |

### Example Data Row
| Column | Value |
|--------|-------|
| ZWEIGSTELLE | Zanklhof |
| SIGNATUR | JK.T PET |
| STANDORT 2 | Ausleihe |
| STATUS | Verfügbar |
| VORBESTELLUNGEN | 0 |
| MEDIENGRUPPE | Kinderbuch |
| FRIST | (empty) |
| BARCODE | 1801SB02708 |

## Status Values
From the observed data:
- **Verfügbar** = Available
- Other possible values:
  - Ausgeliehen = Checked out
  - In Bearbeitung = Processing
  - Vermisst = Lost/Missing
  - Beschädigt = Damaged

## Key Fields for Reservation Functionality
1. **Book Identifier**: ISBN or Catalog ID
2. **Branch Selection**: Must show available branches
3. **User Email**: Required for notification
4. **Optional Fields**:
   - Pickup Location (which branch)
   - Notification Preferences
   - Special Requests/Notes

## Key Fields for Mail Order Functionality
1. **Book Identifier**: ISBN (978-3-8332-3580-1)
2. **Recipient Name**: Required
3. **Recipient Email**: Required
4. **Recipient Phone**: Optional
5. **Delivery Options**:
   - Postal Address (for shipping)
   - Pickup at Branch (pickup location)
6. **Additional Info**:
   - Special Requests
   - Preferred Delivery Date

## Implementation Notes

### For Reservations:
- Reserve button uses ASP.NET postback: `__doPostBack('...BtnReserve','')`
- This suggests form submission rather than direct API
- Will need to simulate form submission in Playwright
- May require additional interaction after clicking (modal/form)

### For Mail Orders:
- Direct link to `/Mediensuche/Postservice`
- Separate page for mail order requests
- Could be filled with prefilled book data via URL parameters

### Data Extraction Priority:
1. ✅ Book metadata (title, author, ISBN, etc.)
2. ✅ Availability status per copy
3. ✅ Branch information
4. ✅ Call numbers/signatures
5. ⚠️ Barcodes (for specific copy selection)
6. ⚠️ Reservation counts

## Next Steps
1. Implement reservation button click handling
2. Explore Postservice form structure
3. Implement form filling for both reservation and mail order
4. Add error handling for duplicates/invalid requests
5. Test with multiple book types
