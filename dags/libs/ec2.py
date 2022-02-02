import logging

logger = logging.getLogger(__name__)

MAX_ELEMENTS = 10

class EC2:

    def __init__(self, account_id, session):
        try:
            self.session = session
            self.client = self.session.client('ec2')
            self.instance_list = []
            self.description_list = []
            self.account_id = account_id
        except Exception as e:
            logger.exception(e)
            raise

    def get_instances_region(self, region):
        """
        Retrieves all the EC2 instances for a region.
        """
        try:
            self.instances_region = []
            conn = self.session.resource('ec2', region_name=region)
            instances = conn.instances.filter()
            for instance in instances:
                self.instances_region.append(instance.id)
        except:
            logger.warn('Ignoring region %s', region)
            pass
        
    def get_instances_description_all(self):
        """
        Splits the fetching of InstanceIds to MAX_ELEMENTS so that in a single call can retrieve
        more than just a single element.
        """
        ec2_regions = [region['RegionName'] for region in self.client.describe_regions()['Regions']]
        for region in ec2_regions:
            self.get_instances_region(region)

            i = 0 
            j = 0
            instance_sublist = []
            for instance in self.instances_region:
                j = j + 1
                instance_sublist.append(instance)
                if i == MAX_ELEMENTS or j == len(self.instances_region):
                    client = self.session.client('ec2', region_name=region)
                    results = client.describe_instances(InstanceIds=instance_sublist)
                    print(results)
                    for m in results["Reservations"]:
                        for n in m["Instances"]:
                            n["AccountId"]=self.account_id
                            self.description_list.append(n)
                elif i < MAX_ELEMENTS:
                    i = i + 1
                else:
                    i = 0
                    instance_sublist = []

if __name__ == '__main__':
    run = EC2(account_id='546429776361')
    run.get_instances_description_all()
    print(run.description_list) 