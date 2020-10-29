### Steps to reproduce debug output:


1. Ensure that getLinks(url, depth)'s depth parameter is 3.

2. Ensure that within start_requests(self), after the array `urls` is built, that the following line is uncommented, and that there are no other print statements.

```python
print("----URLs: ", set(urls))
```

3. Finally, run.

```bash
scrapy crawl sublinks -s LOG_ENABLED=False > sublink_depth_3_output.txt
```

