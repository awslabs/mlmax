# ML technology best practices

Delivering ML solutions to production is hard. It is difficult to know where to start, what tools to use, and whether you are doing it right. Often each individual professional does it a different way based on their individual experience or they use prescribed tools developed within their company. Either way this requires a lot of investment of time to firstly decide what to do and secondly to implement and maintain the infrastructure. There are many existing tools that make parts of the process faster but many months of work is still required to tie these together to deliver robust production infrastructure.

This project provides an example so you can get started quickly without having to make many design choices. The aim is to standardize the approach and hence achieve efficiency in delivery. There are nine independent yet coherent modules: 

## ML inference pipeline
```python
import foobar

foobar.pred('word') # returns 'words'
foobar.pred('goose') # returns 'geese'
foobar.pred('phenomena') # returns 'phenomenon'
```