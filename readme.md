# Identified Need
Canticum Chamber Choir was founded in Brisbane, Australia in 1995. Each year, the choir has its own concert series, and sings in professional engagements with other arts organisations. Over time, various methods have been tried to keep a record of what repertoire has been performed where and when. These methods have included text descriptions on 'Archive' pages of the choir's website; a collection in Dropbox of concert programmes, some of which were just scanned pages; and a spreadsheet with forms for data entry. None of these sources of information were complete. Data in the spreadsheet was the most consistent; for example, in the names of composers. However, data entry was slow, and data was stored multiple times; for example, if we had performed multiple compositions by the one composer, or performed a composition multiple times. Neither could data be easily aggregated; for example, to determine which compositions had been performed most often.

# Solution Summary
I developed a database-driven webapp using Flask and Python. Registered users can create, view, update and delete information about Canticum's repertoire. The display of the data makes it possible to view all composers, compositions, venues, concerts or performances. Via these pages, new data can be entered for the applicable type. Having the data entry on the same page as the display of the data reduces the risk of duplicate data entry. Subsets of the data are also available to answer questions like "What compositions by this composer has Canticum performed?" or "What else was on the programme when Canticum first performed this composition?"

# Database Structure
Data can be entered for:
* Users (username, password)
* Composers (name)
* Compositions (name, composer ID)
* Venues (name)
* Concerts (date, name, venue ID)
* Performances (concert ID, composition ID)
Using ID fields means that no item of data is stored twice.
User passwords are stored hashed.

# Back-End
## Technologies
The application is written in Python. Apology error messages are rendered with a third-party meme-generator service.
## Queries
The application uses CD50's SQL library. Wherever a query needs to be reused, it has been created as a reusable method.
## Methods
Several endpoints have both GET and POST methods.
Get is used when:
* An endpoint is accessed for data display
* An icon is clicked for more information about an data object, or to edit or delete a data object
Post is used when:
* A form is submitted for new data entry
* A form is submitted for editing existing data
## Server-side validation
Forms are only processed if all fields are complete.
Deletion of data is only allowed if there is no dependent data. For example, a venue cannot be deleted if a concert uses that venue. If there is dependent data, a descriptive error message is flashed to the front-end.

# Front-End
## Technologies
The front-end of the webapp is a website rendered with templates using the Flask framework and Jinja2 for data fields and arrays. CSS is using Bootstrap. Icons are created using Font Awesome.
## Authentication
Logging in is not required to view the data. Only logged in users can create, modify or delete data.
Only a logged in user can add a new user or change user passwords.
This approach has been taken to limit the people who can manage the data.
## Data Display
Data is displayed in tables, with sorting controlled by the ordering in the database query.
The index page displays all compositions with the date of its latest performance.
In addition to the full lists of composers, compositions, venues, concerts and performances, the following subsets of data can be displayed:
* Compositions by a selected composer
* Concerts that include a selected compostition
* Concerts at a selected venue
* Programme of a selected concert
## Data Creation
Only logged in users can create, modify or delete data.
Data entry is simplified with drop-down lists. For example, when entering a composition, the user selects the composer's name from a list. For some lists, data is concatenated. For example, when entering a performance, the concert selection list displays a combination of the date and concert name, and the composition selection list displays a combination of the composer and composition names. This concatenation has the advantages of ensuring valid data entry, and reducing the number of selections that must be made. The disadvantage is that some selection lists are long, and methods to optimise this may be needed in future. Possible optimisations include indexing tables for faster data loading, and changing the selection lists to allow filtering by text entry.
## Data Updates
Clicking an Edit icon for a data object opens a form that displays existing data and allows that data to be updated.
## Data Deletion
Clicking a Delete icon for a data object deletes the data if there is no dependent data. This check for dependencies is server-side. There is no confirmation message before deletion.

# Possible Future Enhancements
* Indexing of database tables
* Refinement of SQL queries to return only required columns
* Deletion confirmation
* Archival of data instead of deletion
* Storage of composer birth and death years
* Storage of which user edited data and when