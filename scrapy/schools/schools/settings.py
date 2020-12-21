# Scrapy settings for schools project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'schools'

SPIDER_MODULES = ['schools.spiders']
NEWSPIDER_MODULE = 'schools.spiders'

# How to log spider output
LOG_ENABLED = True
LOG_LEVEL = 'INFO'
LOG_FILE = 'schoolspider_log.log'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'schools (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'


# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares. These are set by default, but explicitly stated for the sake of highlighting what needs configuration.
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.depth.DepthMiddleware': 100, 'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 200, 'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 300
  
}

# Configure depth 
DEPTH_LIMIT = 5


# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'schools.middlewares.SchoolsDownloaderMiddleware': 543, 'scrapy.downloadermiddlewares.retry.RetryMiddleware': 4
}

# Configure times retried after receiving an error
RETRY_TIMES = 5

# Configure delay before downloading.
DOWNLOADS_DELAY = 10

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'schools.pipelines.MyImagesPipeline': 1,
    'schools.pipelines.MyFilesPipeline': 2
}
#    'schools.pipelines.MongoDBPipeline': 3, 

# running locally without containers
# MONGO_URI = 'mongodb://localhost' 
# connect to MongoDB which is running in mongodb_container.
#MONGO_URI = 'mongodb://mongodb_container:27017'

#MONGO_DATABASE = 'schoolSpider' # database (not collection) name


IMAGES_STORE = 'images'
FILES_STORE = 'files'

FILES_EXPIRES = 365
IMAGES_EXPIRES = 365
MEDIA_ALLOW_REDIRECTS = True
IMAGES_MIN_HEIGHT = 150
IMAGES_MIN_WIDTH = 150

