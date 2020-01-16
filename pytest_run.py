#  coding=utf8
import pytest
import  allure

class TestMain(object):

    def setup_class(self):
        self.a = 'aaaaa'
        print("------ setup before class UserLogin ------")

    @allure.story('001')
    def test_sample_1(self):
        allure.attach('杨婷婷')

        assert 'hello' in 'hello world'

    @allure.story('002')
    def test_sample_2(self):
        assert 'OK' in 'are you ok?'

if __name__ == '__main__':
    import os
    pytest.main(['-s', '-q', 'pytest_run.py','--alluredir', './result/'])
    os.system('allure serve ./result/')






