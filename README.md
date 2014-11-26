Callback Nanny
==============

Poor man's webhook receiver.

This is a simple fun-proj to enable self-hosted
[readthedocs](https://readthedocs.org/)-ish continuous documentation generation,
without using CI.

To validate the input request, I use several input mustache templates
with regex to match and transform the request data.

To execute user-defined job, I also use mustache template to generate
shell script.

the hosted API is:

```
/nanny.json
```

which does these things:
  1. receive a posted webhook, only json data supported
  2. peek is a list of template-regex pair. for each pair:
    1. use mustache to render each template
    2. regex to match rendered string
    3. if no match, the request is ignored
    4. update the request data with the match's groupdict
  3. render shell-script template use updated data
  4. run the rendered script (`subprocess.Popen(shell=True)`)
