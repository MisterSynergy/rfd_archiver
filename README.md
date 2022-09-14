# rfd_archiver
Wikidata bot that archives closed sections from [Wikidata:Requests for deletions](https://www.wikidata.org/wiki/Wikidata:Requests_for_deletions)

## Technical requirements
The bot is currently scheduled to run every six hours on [Toolforge](https://wikitech.wikimedia.org/wiki/Portal:Toolforge) from within the `msynbot` tool account. It depends on the [shared pywikibot files](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Pywikibot#Using_the_shared_Pywikibot_files_(recommended_setup)) and is running in a Kubernetes environment using Python 3.9.2.