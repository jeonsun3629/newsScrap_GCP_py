import os
import argparse
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 ID 환경 변수에서 가져오거나 직접 설정
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'newsscrap-456607')
REGION = os.getenv('REGION', 'asia-northeast3')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'newsscrap-service')
SERVICE_URL = os.getenv('SERVICE_URL', f'https://{SERVICE_NAME}-d6vnai5jda-du.a.run.app')

def create_or_update_scheduler(job_name='newsscrap-daily', schedule='0 7 * * * ', uri=None, method='GET', time_zone='Asia/Seoul'):
    """Cloud Scheduler 작업을 생성하거나 업데이트합니다."""
    if uri is None:
        uri = SERVICE_URL
    
    # 기존 작업이 있는지 확인
    check_cmd = f"gcloud scheduler jobs describe {job_name} --project={PROJECT_ID} --location={REGION}"
    
    try:
        subprocess.check_output(check_cmd, shell=True, stderr=subprocess.STDOUT)
        job_exists = True
    except subprocess.CalledProcessError:
        job_exists = False
    
    if job_exists:
        # 기존 작업 업데이트
        cmd = f"""
        gcloud scheduler jobs update http {job_name} \
            --schedule="{schedule}" \
            --uri="{uri}" \
            --http-method={method} \
            --time-zone="{time_zone}" \
            --project={PROJECT_ID} \
            --location={REGION}
        """
        print(f"기존 스케줄러 작업 '{job_name}'을 업데이트합니다...")
    else:
        # 새 작업 생성
        cmd = f"""
        gcloud scheduler jobs create http {job_name} \
            --schedule="{schedule}" \
            --uri="{uri}" \
            --http-method={method} \
            --time-zone="{time_zone}" \
            --project={PROJECT_ID} \
            --location={REGION}
        """
        print(f"새 스케줄러 작업 '{job_name}'을 생성합니다...")
    
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"스케줄러 작업이 성공적으로 {'업데이트' if job_exists else '생성'}되었습니다.")
        print(f"일정: {schedule} ({time_zone})")
        print(f"URI: {uri}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"오류 발생: {e}")
        return False

def delete_scheduler(job_name='newsscrap-daily'):
    """Cloud Scheduler 작업을 삭제합니다."""
    cmd = f"gcloud scheduler jobs delete {job_name} --project={PROJECT_ID} --location={REGION} --quiet"
    
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"스케줄러 작업 '{job_name}'이 삭제되었습니다.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"오류 발생: {e}")
        return False

def run_now(job_name='newsscrap-daily'):
    """Cloud Scheduler 작업을 즉시 실행합니다."""
    cmd = f"gcloud scheduler jobs run {job_name} --project={PROJECT_ID} --location={REGION}"
    
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"스케줄러 작업 '{job_name}'이 실행되었습니다.")
        print(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"오류 발생: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Google Cloud Scheduler 관리 스크립트')
    subparsers = parser.add_subparsers(dest='command', help='명령')
    
    # create 명령 설정
    create_parser = subparsers.add_parser('create', help='스케줄러 작업 생성 또는 업데이트')
    create_parser.add_argument('--name', default='newsscrap-daily', help='작업 이름')
    create_parser.add_argument('--schedule', default='0 7 * * * ', help='cron 형식 스케줄 (기본값: 매일 오후 8시 40분)')
    create_parser.add_argument('--uri', default=None, help='호출할 URI')
    create_parser.add_argument('--method', default='GET', choices=['GET', 'POST'], help='HTTP 요청 메서드')
    create_parser.add_argument('--time-zone', default='Asia/Seoul', help='시간대')
    
    # delete 명령 설정
    delete_parser = subparsers.add_parser('delete', help='스케줄러 작업 삭제')
    delete_parser.add_argument('--name', default='newsscrap-daily', help='작업 이름')
    
    # run 명령 설정
    run_parser = subparsers.add_parser('run', help='스케줄러 작업 즉시 실행')
    run_parser.add_argument('--name', default='newsscrap-daily', help='작업 이름')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_or_update_scheduler(
            job_name=args.name,
            schedule=args.schedule,
            uri=args.uri,
            method=args.method,
            time_zone=args.time_zone
        )
    elif args.command == 'delete':
        delete_scheduler(job_name=args.name)
    elif args.command == 'run':
        run_now(job_name=args.name)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 