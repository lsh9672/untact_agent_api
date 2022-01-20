from ScpTest import SSHManager
import os 

rasb_flask_path = "/home/soda/.untect_center/flask_api/"
# rasb_ORM_path = "/home/soda/.untect_center/flask_api/ORM/"

local_one_connection_flask_path = os.getcwd()+"/flask_api"
local_two_connection_flask_path = os.getcwd()+"/flask_api2"

#config파일
one_flask_config = os.getcwd()+"/config_one"
two_flask_config = os.getcwd()+"/config_two"

def first_one_deploy(start_ip,last_ip):
    try:
        for i in range(start_ip,last_ip+1):
            ssh_manager = SSHManager()
            ssh_manager.create_ssh_client("ip","ssh 계정명","비밀번호", "포트번호")
            #디렉토리 생성
            ssh_manager.send_command("mkdir -p .untect_center/flask_api/")

            '''플라스크 관련코드 생성'''
            for j in os.listdir(local_one_connection_flask_path):
                #.py, .txt 파일만 옮김
                if os.path.splitext(j)[1] == ".py" or os.path.splitext(j)[1] == ".txt":
                    ssh_manager.send_file(local_one_connection_flask_path+"/"+j, rasb_flask_path)

                

            #config 파일
            ssh_manager.send_file(os.getcwd()+"/config_one/"+str(i)+".py",rasb_flask_path+"config.py")

            ssh_manager.send_command("sudo apt update")
            ssh_manager.send_command("sudo apt install python3-pymssql -y")

            ssh_manager.send_file(os.getcwd()+"/only_flask.service", "/home/soda/")
            ssh_manager.send_command("sudo mv only_flask.service /etc/systemd/system")

            ssh_manager.send_command("pip3 install -r /home/soda/.untect_center/flask_api/requirements.txt")
            ssh_manager.send_command("sudo systemctl start only_flask.service")
            ssh_manager.send_command("sudo systemctl enable only_flask.service")

            ssh_manager.close_ssh_client()
    except Exception as ex:
        return ex
    return "success"

#커넥션 2개짜리(148~150)
def first_two_deploy(start_ip,finished_ip):
    # try:
    for i in range(start_ip,finished_ip+1):
        ssh_manager = SSHManager()
        ssh_manager.create_ssh_client("ip","ssh 계정명","비밀번호", "포트번호")
        ssh_manager.send_command("mkdir -p .untect_center/flask_api/")

        '''플라스크 관련코드 생성'''
        for j in os.listdir(local_two_connection_flask_path):
            #.py, .txt 파일만 옮김
            if os.path.splitext(j)[1] == ".py" or os.path.splitext(j)[1] == ".txt":
                ssh_manager.send_file(local_two_connection_flask_path+"/"+j, rasb_flask_path)
            # #디렉토리이면 그 안의 파일을 하나씩 전송하기 위해서
            # elif os.path.splitext(j)[1] == '':
            #     for k in os.listdir(local_two_connection_flask_path+'/'+j):
            #         if os.path.splitext(k)[1] == ".py":
            #             ssh_manager.send_file(local_two_connection_flask_path+"/"+j+"/"+k, rasb_ORM_path)

        #config 파일
        ssh_manager.send_file(os.getcwd()+"/config_two/"+str(i)+".py",rasb_flask_path+"config.py")

        ssh_manager.send_command("sudo apt update")
        ssh_manager.send_command("sudo apt install python3-pymssql -y")

        ssh_manager.send_file(os.getcwd()+"/only_flask.service", "/home/soda/")
        ssh_manager.send_command("sudo mv only_flask.service /etc/systemd/system")
        ssh_manager.send_command("pip3 install -r /home/soda/.untect_center/flask_api/requirements.txt")
        ssh_manager.send_command("sudo systemctl start only_flask.service")
        ssh_manager.send_command("sudo systemctl enable only_flask.service")

        ssh_manager.close_ssh_client()
    # except Exception as ex:
    #     return ex
    return "success"


#커넥션 1개짜리 - 초기 셋팅이 아닐떄
def one_connection(start_ip,last_ip):
    try:
        for i in range(start_ip,last_ip+1):
            ssh_manager = SSHManager()
            ssh_manager.create_ssh_client("ip","ssh 계정명","비밀번호", "포트번호")
            

            '''플라스크 관련코드 생성'''
            for j in os.listdir(local_one_connection_flask_path):
                #.py, .txt 파일만 옮김
                if os.path.splitext(j)[1] == ".py" or os.path.splitext(j)[1] == ".txt":
                    ssh_manager.send_file(local_one_connection_flask_path+"/"+j, rasb_flask_path)


            #config 파일
            ssh_manager.send_file(os.getcwd()+"/config_one/"+str(i)+".py",rasb_flask_path+"config.py")

            ssh_manager.send_command("pip3 install -r /home/soda/.untect_center/flask_api/requirements.txt")
            ssh_manager.send_command("sudo systemctl restart only_flask.service")
            ssh_manager.close_ssh_client()
    except Exception as ex:
        return ex
    return "success"

#커넥션 2개짜리(148~150), 초기 셋팅이 아닐떄
def two_connection(start_ip,finished_ip):
    try:
        for i in range(start_ip,finished_ip+1):
            ssh_manager = SSHManager()
            ssh_manager.create_ssh_client("ip","ssh 계정명","비밀번호", "포트번호")

            '''플라스크 관련코드 생성'''
            for j in os.listdir(local_two_connection_flask_path):
                #.py, .txt 파일만 옮김
                if os.path.splitext(j)[1] == ".py" or os.path.splitext(j)[1] == ".txt":
                    ssh_manager.send_file(local_two_connection_flask_path+"/"+j, rasb_flask_path)

            #config 파일
            ssh_manager.send_file(os.getcwd()+"/config_two/"+str(i)+".py",rasb_flask_path+"config.py")

            ssh_manager.send_command("pip3 install -r /home/soda/.untect_center/flask_api/requirements.txt")
            ssh_manager.send_command("sudo systemctl restart only_flask.service")

            ssh_manager.close_ssh_client()
    except Exception as ex:
        return ex
    return "success"

#config파일 생성
def config_create(type,start_ip,finished_ip):
    #1이면 1개짜리 
    if type == 1:
        config_dir = os.getcwd()+"/config_one/"
        for i in range(start_ip,finished_ip+1):
            with open(f"{config_dir}{i}.py","w") as f:
                f.write(f'ipynb_save_file_path = "/home/soda/Project/python/notebook/workbook.ipynb"\
                    \n\n# md file path\
                    \nmd_save_file_path = "/home/soda/Project/python/notebook/book.md"\
                    \n\n# lecture file path\
                    \nlecture_file_path = "/home/soda/.untect_center/lecture/"\
                    \njupyter_port = "포트번호"\
                    \nweb_server_ip = "ip번호"\
                    \nweb_server_port = "포트번호"\
                    \n\n#device info\
                    \ncamera_ip = "ip번호"\
                    \ndevice_ip = "ip번호"')

    #2면 2개짜리
    elif type ==2:
        config_dir = os.getcwd()+"/config_two/"
        for i in range(start_ip,finished_ip+1):
            with open(f"{config_dir}{i}.py","w") as f:
                f.write(f'ipynb_save_file_path = "/home/soda/Project/python/notebook/"\
                    \n\n# md file path\
                    \nmd_save_file_path = "/home/soda/Project/python/notebook/book.md"\
                    \n\n# lecture file path\
                    \nlecture_file_path = "/home/soda/.untect_center/lecture/"\
                    \njupyter_port = "포트번호"\
                    \nweb_server_ip = "ip번호"\
                    \nweb_server_port = "포트번호"\
                    \n\n#device info\
                    \ncamera_ip = "ip번호"\
                    \ndevice_ip = "ip번호"')

    
if __name__ == "__main__":
    # config_create(1,131,150)
    # config_create(2,154,163)
    # first_two_deploy(158,163)
    # first_one_deploy(147,148)
    # one_connection(145,145)
    # one_connection(150,150)
    # config_create(2,165,170)
    # two_connection(165,170)
    # one_connection(145,150)
    # config_create(1,177,177)
    one_connection(177,177)
