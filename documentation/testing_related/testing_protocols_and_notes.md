# Testing Protocols & Notes

---
*This file contains protocols, conventions, best practices, and miscellaneous notes. For quick start, infrastructure, or coverage, see the other docs in this folder.*

Testing Protocol for Operator Portal Functionality

1. (Optional) Clear logs from:
    C:\one_drive\code\pycharm\feedback_portal\logs
    C:\one_drive\code\pycharm\feedback_portal\source\production\arb\logs

2. Launch portal
    from laptop:
        cd "C:\one_drive\code\pycharm\feedback_portal\source\production\arb"
        flask --app wsgi run --debug --no-reload
    from ec2:
        git checkout qa_qc_of_stable_system_01
        git fetch --all --prune
        git pull
        cd "/home/theld/code/git_repos/feedback_portal/shell_scripts"
        ./launch_with_screen.sh

3. Confirm logging file is created and logging as expected:
    from laptop:
        dir "C:\one_drive\code\pycharm\feedback_portal\source\production\arb\logs\"
    from ec2:
        cd "/home/theld/code/git_repos/feedback_portal/logs/"
        ls "/home/theld/code/git_repos/feedback_portal/logs/"
        head -n 2 arb_portal.log
        tail -n 2 arb_portal.log

4. Check that you can click all diagnostic menus and test search
    pass

5. Click the top 3 incidents in the index to make sure they work and that their summary data is populating properly
    pass

6. Create a new oil & gas incident
    - check to see if an initial data population with dummy data makes sense
        created: id 1001
    - delete all data except the incidence id and validate
        pass
    - populate all fields with new values then validate
        pass
    - make sure all fields are persisting
        pass

7. Create a new landfill incident
    - check to see if initial data population with dummy data makes sense
        pass
    - delete all data except the incidence id and validate
        pass
    - populate all fields with new values then validate
        pass
    - make sure all fields are persisting
        pass

8. Create example templates for both oil and gas and landfill with all blank entries except for id_incident
    - drop these into the spreadsheet reader and make sure they populate persist
      - landfill
          pass
      - oil and gas
          pass

9. Create example templates for both oil and gas and landfill with all populated entries
    - drop these into the spreadsheet reader and make sure they populate persist
      - landfill
          pass
      - oil and gas
          pass

10. Use the excel jinja templates, that still have {{ variable }} notation and see what happens when you drop them in
    make sure to populate the id_incident or else it will make work for dan
    - drop these into the spreadsheet reader and make sure they populate persist
      - landfill
          pass
      - oil and gas
          pass

11. Create example templates for both oil and gas and landfill with deliberately incorrect data types
    - Date fields
        use incorrectly formated date strings
        put in words rather than date information
    - Number fields
        put in blank strings and/or words
    - drop these into the spreadsheet reader and make sure they populate persist and log failure warnings

12. Oil and Gas Contingent Drop-downs
    - Make sure any contingent drop-downs are working as expected
    - Make a list of all logic rules and make sure each is enforced

13. Landfill Validation Contingent Drop-downs
    - Make sure any contingent drop-downs are working as expected
    - Make a list of all logic rules and make sure each is enforced

14. Oil and Gas additional validation
    - List and verify

15. Landfill additional validation
    - List and verify

16. Compile QA/QC and rerun stack

17. Auto-create site documentation and serve

18. Try to automate unit testing


Implementing testing 05/14/25

Refactered and retesting 6/2/25
1. creating 2001, make sure portal changes update and logging still works.
2. clear out all values - test logging, portal changes
3. check usage now that it is mostly blank
4. repopulate and make sure it persists
6. same with 2002
7. add all the test spreadsheets
8. 


5. loop through all incidences and make sure you don't get any sector or sector_type not found errors

it is a little confusing on how some things go from None to blank string ... 