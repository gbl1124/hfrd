# 1.1.0 (2020-09-16)
### New future : Support IBP V2.5 create network
* ** update peer config file, node.js and support 1.4.7-1
.
# 1.0.7 (2020-06-17)
### New future : reduce delay for multiple run
* ** add preruntest.yml and move prepare task into preruntest.yml to reduce delay time.

# 1.0.6 (2020-06-09)
### Fix Bug
* ** alpine version: change alpine verfion from latest to 3.9.5 which support python2.

# 1.0.5 (2020-06-08)
### New future
* ** enable "default" namespace: When testplan.yml out of specified "namespace", test will run test with "default" namespace on K8S test claster.

# 1.0.4 (2020-06-04)
### New future
* ** customized "intervalNum" added in testplan.yml. if not used the keyword, will used default intervals(from frist interval to last but one interval) to summary TPS.
* ** customized "namespace" added in testplan.yml. The runtest will use testplan.yml specified "namespace" on K8S test claster

# 1.0.3 (2020-06-03)

### New future
* **Summary TPS**: Changed interval time(endtime - starttime)/10 to 15s


# 1.0.2 (2020-06-01)

### Bug Fixes
* **grafana**: Fix grafana PDF not show. Using grafana/grafana:6.7.0 instead of grafana/grafana:latest
* **peer name**: HFRD could not run test case after manually create the channel，after double confirm used full peer names.

# 1.0.1 (2020-05-29)

### New future
* **HSM**: remove HSM function from the master and create a branch named icphsm
