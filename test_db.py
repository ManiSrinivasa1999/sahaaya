#!/usr/bin/env python3
"""Test the offline database guidance"""

from app.db import OfflineHealthDatabase

db = OfflineHealthDatabase()

print('=' * 70)
print('Testing Offline Database Guidance')
print('=' * 70)

print('\n1. Fever Query:')
result = db.get_offline_health_guidance('I have fever', 'en')
print('Guidance:', result.get('guidance')[:200])
print('Severity:', result.get('severity'))
print('Possible conditions:', result.get('possible_conditions'))
print('Home treatment:', result.get('home_treatment'))

print('\n2. Chest Pain Query:')
result = db.get_offline_health_guidance('chest pain', 'en')
print('Guidance:', result.get('guidance')[:200])
print('Severity:', result.get('severity'))
print('Possible conditions:', result.get('possible_conditions'))

print('\n3. Emergency Heart Attack Query:')
result = db.get_offline_health_guidance('heart attack', 'en')
print('Guidance:', result.get('guidance')[:200])
print('Severity:', result.get('severity'))

print('\n4. Headache Query:')
result = db.get_offline_health_guidance('headache', 'en')
print('Guidance:', result.get('guidance')[:200])
print('Severity:', result.get('severity'))

print('\n✅ Database test complete')
