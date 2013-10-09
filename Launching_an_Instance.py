#!/usr/bin/env python

import os
import time
import boto
import boto.manage.cmdshell
import keypair_create from keypair_create
import security_group from security_group


def launch_instance(ami='ami-35792c5c',
	instance_type='t1.micro',
	key_name='igor_keyname',  #will be created if it does not exist
	key_extension='.pem',
	key_dir='~/.ssh',
	group_name='igor_sg', #will be created if it does not exist
	from_port=0,
	to_port=65535,
	cidr1='192.116.128.82/32',   #limit access to your instance
	cidr2='84.94.114.231/32',
	tag='igor-ami-35792c5c', 
	user_data=None,
	cmd_shell=True,
	login_user='ec2-user',
	ssh_passwd=None):

	cmd = None

# CREATE A CONNECTIONS to EC2 service.
	try:
		ec2 = boto.connect_ec2()
	except: 
		print 'Cannot connect to EC2 service'
		raise


#CREATING SSH KEYPAIR
	try:
		key = ec2.get_all_key_pairs(keynames=[key_name])[0]
	except ec2.ResponseError, e:
		if e.code in ['InvalidKeyPair.Duplicate', 'InvalidKeyPairFormat', 'InvalidKeyPair.NotFound']:		
			print 'Creating keypair: %s' % key_name
			keypair_create(key_name)
		else:
			raise
			

#SECURITY GROUP
	try:
		group = ec2.get_all_security_groups(groupnames=[group_name])[0]
	except ec2.ResponseError, e:
		if e.code == 'InvalidGroup.NotFound':
			print 'Creating Security Group: %s' % group_name
			security_group(group_name)
		else:
			raise

# ADD a rule to the security group
	try:
		group.authorize('tcp', from_port, to_port, cidr1)
		group.authorize('tcp', from_port, to_port, cidr2)
	except ec2.ResponseError, e:
		if e.code == 'InvalidPermission.Duplicate':
			print 'This rule is already authorized'
		else:
			raise



#START UP THE INSTANCE
	reservation = ec2.run_instances(ami,
		key_name=key_name,
		security_groups=[group_name],
		instance_type=instance_type,
		user_data=user_data)

# Find the actual Instance object inside the Reservation object
# returned by EC2.
	instance = reservation.instances[0]

# The instance has been launched but it's not yet up and
# running. Let's wait for its state to change to 'running'.
	print 'Waiting for instance'
	while instance.state != 'running' or instance.state != 'terminated':
		print '.'
		time.sleep(5)
		instance.update()
	print 'Done'


#ADD TAGS
	try:
		instance.add_tag(tag)
	except instance.ResponseError, e:
		if e.code == 'TagLimitExceeded':
			print 'You have reached the limit on the number of tags'
		else:
			raise

# The instance is now running, let's try to programmatically
# SSH to the instance using Paramiko via boto CmdShell.
	if cmd_shell:
		key_path = os.path.join(os.path.expanduser(key_dir),
			key_name+key_extension)
		cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
			key_path,
			user_name=login_user)
	return (instance, cmd)
