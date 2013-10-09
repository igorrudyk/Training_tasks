#!/usr/bin/env python

import os
import boto

def security_group(group_name):

	def security_group(group_name):
		result = true
		try
			group = ec2.create_security_group(group_name)
		except	ec2.ResponseError, e:	
			if e.code == 'InvalidKeyPair.Duplicate':
				result = false
			else 
				raise		
		return result
		
	
	while True:
		success = security_group(group_name)
		if success:
			break	
		else 
	 		security_group=raw_input('Enter new group name').strip()
