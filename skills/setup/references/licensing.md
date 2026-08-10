# How to set up license files in git projects

Do not change existing license files. Unlike the other metadata files, this one is not checked for currency: changing a project's license has legal consequences for everyone who already relied on it, and that is not an agent's call. Leave it exactly as it is, even if it looks stale.

If the project has no license file that should be added.

If the applicable license and copyright is already clearly specified in the readme, add the right file, renamed to `LICENSE`:

* [MIT License](../assets/MIT-LICENSE-template.txt), with the <Copyright> line fixed
* [Apache License, v2.0](../assets/APACHE-LICENSE.txt), renamed to `LICENSE`
* [Proprietary License](../assets/PROPRIETARY-LICENSE-template.txt), with the <Copyright> line fixed

If the license is not specified yet, lead with the recommendation so the user can accept it in a word: **Apache License, v2.0** if the project is public, **proprietary** otherwise. Ask, but ask as "Apache-2.0, since this repo is public — ok?" rather than as an open question.

Ask the user what copyright line should be used, do not guess. Expect an answer like `Copyright <YYYY> <Name>`, though the specifying the year is optional.

## NOTICE files

If the apache license is used, there can be a NOTICE file. That is where copyright mentions and attributions can go. Notices can never be removed, so it is preferred not to have the file or otherwise for it to have minimal content only.

# Deciding on an open source license

_Actually_ choosing and implementing a license policy is real work, most of it for humans.

Setting up the basic LICENSE file helps the humans to get started, and the Apache License, v2.0 is a good default choice.

The [opensource legal guide](https://opensource.guide/legal/) is good. Refer users to it if they ask for advice.
