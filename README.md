# "Kaskeda"

At the moment, this is a project investigating media, information
diffusion, propaganda, and polarization on [reddit]. The data being
used mostly comes from [Pushshift], which is maintained by Jason
Baumgartner.

The software in this repository is designed to facilitate high-scale
analytics on reddit data. It has been tested on a server with 64 cores
and can iterate through almost the entire history of reddit
submissions (2005-2017) in under a minute.

---

## Why?

According to a [2017 Pew Research Center report][pew2017], 6% of U.S.
adults use reddit and 4% of U.S. adults get news from the site.

---

## Set up

Reddit archives can be obtained from [Pushshift]. The [file server]
contains a mostly complete dataset of reddit comments, submissions,
and subreddits.

```sh
git clone git@github.com:CarlColglazier/kaskeda.git
cd kaskeda
mkdir data
```


[reddit]: https://reddit.com/ "reddit: the front page of the internet"

[Pushshift]: https://pushshift.io/

[file server]: https://files.pushshift.io/reddit/

[pew2017]: http://www.journalism.org/2017/09/07/news-use-across-social-media-platforms-2017/
