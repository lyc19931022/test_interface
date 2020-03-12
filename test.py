
# -- coding: utf-8 --
'''
Created on 2019年3月26日

@author: lyc
'''
import pytest
import allure


@allure.feature('Testing')
class TestSample(object):

    def setup_class(self):
        self.a = 'aaaaa'
        print("------ setup before class UserLogin ------")

    @allure.story('001')
    def test_sample_1(self):
        assert True


if __name__ == '__main__':
    import os

    pytest.main(['-s', '-q', 'test.py', '--alluredir', './result/'])
    os.system('allure serve ./result/')

