import newspaper


def init_config():
    config = newspaper.Config()
    config.fetch_images = False
    config.verbose = True

    return config


def parse_article(url):
    a = newspaper.Article(url, init_config())
    a.download()
    a.parse()

    return a
