#!/usr/bin/env python

import os
import boto

def keypair_create(key_name):

	def keypair_create(key_name):
		result = true;
		try:
			key = ec2.create_key_pair(key_name)
			key.save(key_dir)
		except	ec2.ResponseError, e:
			if e.code == 'InvalidKeyPair.Duplicate':
				result = false;
				print 'result=false'
			else: 
				raise		
		return result;
		
	
	while True:
		success = keypair_create(key_name)
		if success:
			break	
		else: 
	 		key_name=raw_input('Enter new key name').strip()
