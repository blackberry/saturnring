## What is where?
0. Detailed Documentation `saturnring/doc/Saturn Cloud Storage Developer and User
   Guide.pdf`
1. Saturnring software `saturnring/ssddj`
2. Development environment setup using Vagrant for Saturnring `saturnring/devenv`
3. OpenNebula driver to use Saturn storage as a data store backend
`saturnring/saturn-opennebula-driver`
4. OpenNebula development environment setup using Vagrant for further
   driver development `saturnring/saturn-opennebula-driver\on-devenv`


## Synopsis

Saturnring enables sharing multiple block storage devices on multiple hosts via iSCSI. For example, SSD or QoS-guaranteed block storage like AWS provisioned IOPs can be shared by multiple VMs using Saturnring. The key design goal is to keep the multiple hosts independent of each other; i.e., each host can break independently and only affect the iSCSI targets on that host. So Saturnring is not a clustered file system; instead think of it as  manager for scaling up and orchestrating many iSCSI servers serving block storage to many clients. 

## Documentation
Updated Documentation for the code and basic usage is available in the /doc folder's [Saturn Cloud Storage Developer and User Guide](doc/Saturn Cloud Storage Developer and User Guide.pdf). (Note link may not work in Gitlab, just browse to the doc subdirectory and open the pdf file)



## Architecture

*Detailed and up-to-date documentation is provided in the file [Saturn Cloud Storage Developer and User Guide](doc/Saturn Cloud Storage Developer and User Guide.pdf) (Note link may not work in Gitlab, just browse to the doc subdirectory and open the pdf file)


Saturnring provides the following components:

1. A web portal and API which allows the storage administrator to manage users and their iSCSI targets
2. A HTTP RESTful-API call to provision iSCSI targets. To keep things simple the API is very sparse by design.
3. Facilities like user quotas, ingesting multiple iSCSI target servers into a Saturnring cluster, deleting storage, encryption, thin provisioning, and basic monitoring support etc. are available via the Saturnring portal
4. Support for VLANs
5. Tracking statistics about usage/quotas etc.

A Vagrant setup where all of the above can be quickly setup; this example should give enough guidance to  install Saturnring in AWS or other suitable public or private cloud provider.

Clients can use the RESTful provisioner call to create iSCSI targets on saturn servers' LVM volume groups. The portal allows administrators to track the overall storage in the Saturnring cluster (up to the logical volume level). It also provides user views to track Saturn storage for individual users. The web portal is a modified Django admin interface. By hacking the default Django interface rather than creating custom views, the core functionlity (managing iSCSI block devices) has been the key development focus. 

## Installation and Getting Started
Saturnring is built out of multiple components - the iSCSI server(s), the Django-driven Saturnring portal and API and Apache webserver with modwsgi extensions, the backend database (sqlite or other Django-compatible relational DB) and a redis-server and job workers for running periodic tasks. A Vagrant file and shell provisioner scripts are included to automatically setup these components for illustration. Instead of supplying pre-baked and customized VM images for quick setup the idea is to provide scripts that can be adapted to instantiate Saturnring on any private or public cloud. The Vagrant file setups up Virtualbox VMs that take on the roles of the Saturnring server, 2 iSCSI servers, and an iSCSI client. Vagrant brings up vanilla Ubuntu 14.04 images, and the shell provisioner scripts do the work of adapting the vanilla VMs into these different roles. These bash scripts are an easy segway to setting up Saturnring in any other virtual or bare-metal environment, or for creating custom images to be used in the cloud.

An unhindered Internet connection and a computer capable of running at least 2 VMs (256M RAM per VM, 1 vCPU per VM, 20GiB disk) is assumed here. 'Host' refers to the PC running the VMs, the SSH login/password for all VMs is vagrant/vagrant, and the Vagrant file defines an internal network 192.168.61/24 and a bridged adaptor to let VMs access the Internet.

For further instructions on the Vagrant setup read the documentation in the chapter titled "Installation Guide" of "Saturn Cloud Storage User Guide.docx" in the /doc directory.

## Deployment Considerations

Here are some ideas for Saturnring in production

1. Monitoring and Alerting - consider something like Zabbix or Nagios to keep tabs on Saturnring components

2. Configuration management (Puppet/Chef etc.) or pre-built images will reduce the pain and errors that come with managing multiple servers manually

3. SSDs wear out - they have limited PE cycles; best to keep a close eye on them  

4. Saturnring uses a recent LVM2 implementation, look at its documentation for its many features

5. The Vagrant example does not patch the Linux kernel for optimal SCST iSCSI target software performance. Read more here: http://scst.sourceforge.net/iscsi-scst-howto.txt

 


## License

Apache 2.0 license
http://www.apache.org/licenses/LICENSE-2.0

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

