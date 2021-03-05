import os
import glob
import smtplib
import os
import cryptocode
import sys

def send_email(rec_email, subject, message):
    
    sender_email = 'cailab_datapipeline@outlook.com'
    
    encoded = 'd11oMDYS+nzpiw==*u3+Z9B/lAtcL4pcQe8okjg==*HTyLRrZj/C3/Yw0DLf7kdQ==*z2WdkXHvk/vOompWCGf0kQ=='
    key = os.environ['EMAIL']
    
    password = cryptocode.decrypt(encoded, key)
    
    message = 'Subject: {}\n\n{}'.format(subject, message)
    server = smtplib.SMTP('smtp.outlook.com', 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, rec_email, message)
    print('Email Sent to', rec_email)

def are_logs_finished(analysis_dir):
    glob_me = os.path.join(analysis_dir, 'MMStack_Pos*', 'Logging.txt')
    
    log_file_paths = glob.glob(glob_me)
    
    bool_pos_done = []
    
    for log_file in log_file_paths:
        file = open(log_file,mode='r')
        content = file.read()
        file.close()
        bool_pos_done.append('Finished with Analysis of Position' in content)
        
    return all(bool_pos_done)

def send_finished_notif(analysis_dir, rec_email):
    
    bool_finished = are_logs_finished(analysis_dir)
    if bool_finished == True:    
        splitted = analysis_dir.split(os.sep)
        print(f'{splitted=}')
        analysis_name = splitted[-1]
        experiment_name = splitted[-2]
        personal = splitted[-3]
        
        subject = 'Analysis of ' + experiment_name + ' is Finished'
        message = 'Your analysis ({}) is located at <b> {}/{}/{} </b> in https://caltech-my.sharepoint.com/personal/nrezaee_caltech_edu/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fnrezaee%5Fcaltech%5Fedu%2FDocuments%2FAnalyses'
        message = message.format(experiment_name, personal, experiment_name, analysis_name)                                                                                                                                                                                             

        send_email(rec_email, subject, message)

if sys.argv[1] == 'debug_email':
    analysis_dir = '/groups/CaiLab/analyses/nrezaee/linus_data/linus_decoding_test'
    rec_email = 'resace3@gmail.com'
    
    send_finished_notif(analysis_dir, rec_email)