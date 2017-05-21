import autoqm.creator
import autoqm.launcher

def main():
	autoqm.creator.create_jobs()
	autoqm.launcher.launch_jobs()

if __name__ == '__main__':
	main()