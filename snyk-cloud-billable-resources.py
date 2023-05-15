import requests
import argparse
import pkg_resources
pkg_resources.require("urllib3==1.26.15")  # Latest supported version
pkg_resources.require("requests==2.28.2")  # Latest supported version


# Description: Snyk Cloud Resources tool to identify and count billable resources via API
# Intent of this tool was to quantify number of billable resources in Snyk Cloud/IaC
# Authors:  Tim Gowan & Ricardo Green

def getCloudResources(orgId, token, billable_resources):
    count = 0
    uri = "https://api.snyk.io/rest/orgs/" + orgId + "/cloud/resources?resource_type=" + billable_resources + \
          "&kind=cloud&removed=false&version=2023-02-15%7Ebeta&limit=100"  # loop through billable_resources
    response = requests.get(url=uri,
                            headers={"Authorization": "token " + token, "Accept": "application/vnd.api+json"}).json()
    for i in response["data"]:
        count += 1
        print("[" + str(count) + "] Resource Type: " + i["attributes"]["resource_type"] + ", Resource ID: " +
              i["attributes"]["resource_id"])

    # Handle Paginated Responses
    while "links" in response:
        uri = "https://api.snyk.io" + response["links"]["next"]
        response = requests.get(url=uri,
                                headers={"Authorization": "token " + token,
                                         "Accept": "application/vnd.api+json"}).json()
        if "data" in response:
            for i in response["data"]:
                count += 1
                print("[" + str(count) + "] Resource Type: " + i["attributes"]["resource_type"] + ", Resource ID: " +
                      i["attributes"]["resource_id"])
    return count


if __name__ == '__main__':
    # Parsing Command Line Arguments
    parser = argparse.ArgumentParser(
        description='Identify projects added at a certain date range based on baseline date range.')
    parser.add_argument('--token', '-t', type=str, help='Snyk user account API token', required=True)
    parser.add_argument('--orgId', '-o', type=str, help='Snyk organization ID', required=True)
    parser.add_argument('--provider', '-p', type=str, help='Cloud Provider: [aws, google, azure, all]',
                        required=True)
    args = parser.parse_args()

    # Enumerate billable resource strings:
    aws_billable_resource_types = ["aws_instance", "aws_lambda_function", "aws_elastic_beanstalk_application",
                                   "aws_ecs_service", "aws_eks_cluster", "aws_db_instance",
                                   "aws_docdb_cluster_instance",
                                   "aws_neptune_cluster_instance", "aws_rds_cluster_instance", "aws_redshift_cluster",
                                   "aws_s3_bucket", "aws_elasticache_cluster"]

    azure_billable_resource_types = ["azurerm_virtual_machine", "azurerm_function_app", "azurerm_app_service",
                                     "azurerm_container_group", "azurerm_kubernetes_cluster",
                                     "azurerm_cosmosdb_account",
                                     "azurerm_cosmosdb_cassandra_cluster", "azurerm_mariadb_server",
                                     "azurerm_mssql_server",
                                     "azurerm_mysql_server", "azurerm_postgresql_server", "azurerm_redis_cache",
                                     "azurerm_sql_server"]
    google_billable_resource_types = ["google_compute_instance", "google_cloudfunctions_function",
                                      "google_cloudfunctions2_function", "google_app_engine_application",
                                      "google_cloud_run_service", "google_container_cluster",
                                      "google_sql_database_instance",
                                      "google_spanner_instance", "google_bigtable_instance", "google_redis_instance",
                                      "google_storage_bucket"]
    # Collect billable resource for cloud provider and reformat to comma-separated string for use in API endpoint
    if args.provider.lower() in ["aws", "amazon"]:
        billable_resources = ','.join(aws_billable_resource_types)
    elif args.provider.lower() in ["azure"]:
        billable_resources = ','.join(azure_billable_resource_types)
    elif args.provider.lower() in ["google", "gcp"]:
        billable_resources = ','.join(google_billable_resource_types)
    elif args.provider.lower() in ["all", "all_supported", "multi-cloud"]:
        billable_resources = ','.join(aws_billable_resource_types
                                      + azure_billable_resource_types
                                      + google_billable_resource_types)
    else:
        print("Unsupported Cloud Provider: " + args.provider)
        exit(1)

    count = getCloudResources(token=args.token, billable_resources=billable_resources, orgId=args.orgId)
    print("")
    print("Billable Resource Count: "+ str(count))
