import json
from django.shortcuts import render
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.http import JsonResponse
from classroom.models import Enrollment
from user.models import CustomUser
from activity.models import Activity
from django.http import HttpRequest
from .utils import IntermediaryUtils, pcUtils
from . import scoring
from ciscoconfparse import CiscoConfParse


# Create your views here.

def RestartActivityView(request, enrollmentID, activityID):
    if request.method == "POST":
        try:
            student = request.user
            enrollment = Enrollment.objects.get(id=enrollmentID)
            activity = Activity.objects.get(id=activityID)

            # Ensure enrollment has a classroom
            if not enrollment.classroom:
                return JsonResponse({"message": "Enrollment does not have a classroom"}, status=400)

            baseProjectID = activity.base_activity.projectID
            name = f"{student.email}_{enrollment.classroom.course.slug}_{enrollment.id}_{activity.mode}"

            request_data = {"name": name}

            response = requests.post(
                f"{settings.SIMULATION_SITE_DOMAIN}v2/projects/{baseProjectID}/duplicate",
                auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD),
                json=request_data
            )

            if response.status_code == 201:
                responseJSON = response.json()
                newProjectID = responseJSON.get("project_id")
                activity.projectID = newProjectID
                activity.save()

                return JsonResponse({"message": "Successfully restarted!"}, status=200)
            else:
                return JsonResponse({"message": "Failed to restart"}, status=401)

        except Enrollment.DoesNotExist:
            return JsonResponse({"message": "Enrollment not found"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


def SaveActivityView(request , activityID):
    activity = Activity.objects.get(id=activityID)
    timeSpent = request.POST.get("timeSpent")

    activity.time_spent = timeSpent
    activity.status = "working"
    activity.save()

    return JsonResponse({"message":"successd"}, status=200)

def ScoresView(request,activityID):
    activity = Activity.objects.get(id=activityID)

    print(1)
    projectID = activity.projectID
    nodes = getAllNodes(projectID)
    print(2)
    allConfigs = getAllNodeConfigs(projectID, nodes)
    print(3)
    allConfigs["links"] = IntermediaryUtils.getAllLinks(projectID, nodes)
    print(4)

    correctConfigString = activity.base_activity.answer_key
    correctConfig = json.loads(correctConfigString)
    correctConfig = json.loads(correctConfig)

    points = scoring.getPoints(allConfigs, correctConfig)

    # print(allConfigs)
    # print(correctConfig)
    # print("")
    print(points)

    return JsonResponse(points)

def SubmitActivityView(request):
    pass




def getAllNodes(projectID):
    responseToOpen = requests.post(settings.SIMULATION_SITE_DOMAIN + "v2/projects/" + projectID + "/open",
        auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD))

    response = requests.get(settings.SIMULATION_SITE_DOMAIN + "v2/projects/" + projectID + "/nodes",
        auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD))
    
    data = response.json()

    routerCounter = 0
    nodeArray = []
    for node in data:
        id = node["node_id"]
        type = None
        nodeProperties = node["properties"]
        if nodeProperties.get("path"):
            if nodeProperties.get("path") == "i86bi-linux-l2-ipbasek9-15.1g.bin":
                type = "switch"
        if nodeProperties.get("image"):
            if nodeProperties.get("image") == "c3725-adventerprisek9-mz.124-15.T14.image":
                type = "router"
                routerCounter = routerCounter + 1
        if node["node_type"] == "vpcs":
                type = "pc"

        if type == "router":
            nodeData = {"name":node["name"], "type": type, "id": id, "router counter": routerCounter}
        else:
            nodeData = {"name":node["name"], "type": type, "id": id}
        nodeArray.append(nodeData)
    
    return nodeArray

def getAllNodeConfigs(projectID, nodes):

    allNodeConfigs = {}
    routerCounter = 1
    for node in nodes:
       
        if node["type"] == "pc":
            pc = getPCConfigToJSONObject(projectID, node)
            allNodeConfigs[node["name"]] = pc
        elif node["type"] == "switch":
            switch = getSwitchConfigToJSONObject(projectID, node)
            allNodeConfigs[node["name"]] = switch
        if node["type"] == "router":
            router = getRouterConfigToJSONObject(projectID, node, routerCounter)
            allNodeConfigs[node["name"]] = router
            routerCounter += 1

    return allNodeConfigs

def getPCConfigToJSONObject(projectID, node):
    response = requests.get(settings.SIMULATION_SITE_DOMAIN + "v2/projects/" + projectID + "/nodes/" + node["id"]+ "/files/startup.vpc",
            auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD))

    return pcUtils.getConfigIP(response.text)

def getSwitchParse(projectID, node):
    response = requests.get(settings.SIMULATION_SITE_DOMAIN + "v2/projects/" + projectID + "/nodes/" + node["id"] +"/files/startup-config.cfg",
            auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD))
    
    parse = CiscoConfParse(response.text.splitlines())
    return parse

def getSwitchConfigToJSONObject(projectID, node):
    parse = getSwitchParse(projectID, node)

    jsonConfig = {}

    jsonConfig["projectID"] = projectID
    jsonConfig["nodeID"] = node["id"]
    jsonConfig["deviceType"] = IntermediaryUtils.getConfigDeviceType(projectID, node)
    jsonConfig["service password-encryption"] = IntermediaryUtils.getConfigServicePasswordEncryption(parse)

    secretPass = IntermediaryUtils.getConfigPrivilegeExecHash(parse)
    if len(secretPass) != 0:
        jsonConfig["enable secret"] = secretPass

    jsonConfig["hostname"] = IntermediaryUtils.getConfigHostname(parse)

    jsonConfig["interfaces"] = IntermediaryUtils.getConfigInterfaces(parse)

    bannerMOTD = IntermediaryUtils.getConfigBannerMOTD(parse)
    if len(bannerMOTD) != 0:
        jsonConfig["banner motd"] = bannerMOTD

    lineConsole = IntermediaryUtils.getConfigConsolePassword(parse)
    if len(lineConsole) != 0:
        jsonConfig["line console"] = lineConsole

    lineVty = IntermediaryUtils.getConfigLineVTY(parse)
    if len(lineVty) != 0:
        jsonConfig["line vty"] = lineVty

    ipDefaultGateWay = IntermediaryUtils.getConfigIPDefaultGateway(parse)
    if ipDefaultGateWay:
        jsonConfig["default gateway"] = ipDefaultGateWay

    localUserAccount = IntermediaryUtils.getLocalUserAccount(parse)
    if localUserAccount:
        jsonConfig["local user account"] = localUserAccount

    ipDomainLookup = IntermediaryUtils.getIPDomainLookup(parse)
    jsonConfig["ip domain-name lookup"] = ipDomainLookup

    ipDomainName = IntermediaryUtils.getIPDomainName(parse)
    if len(ipDomainName) != 0:
        jsonConfig["ip domain-name"] = ipDomainName

    dhcp = IntermediaryUtils.getDHCP(parse)
    if len(dhcp) != 0:
        jsonConfig["dhcp"] = dhcp

    vlan = IntermediaryUtils.getConfigVlan(parse)
    if len(vlan) != 0:
        jsonConfig["vlan"] = vlan

    return jsonConfig

def getRouterParse(projectID, node, routerCounter):
    response = requests.get(settings.SIMULATION_SITE_DOMAIN + "v2/projects/" + projectID + "/nodes/" + node["id"] +"/files/configs/i"+ str(routerCounter) +"_startup-config.cfg",
            auth=HTTPBasicAuth(settings.SIMULATION_AUTH_USERNAME, settings.SIMULATION_AUTH_PASSWORD))
    parse = CiscoConfParse(response.text.splitlines())

    return parse

def getRouterConfigToJSONObject(projectID, node, routerCounter):
    
    parse = getRouterParse(projectID, node, routerCounter)
    print(routerCounter)

    jsonConfig = {}

    jsonConfig["projectID"] = projectID
    jsonConfig["nodeID"] = node["id"]
    jsonConfig["deviceType"] = IntermediaryUtils.getConfigDeviceType(projectID, node)
    jsonConfig["service password-encryption"] = IntermediaryUtils.getConfigServicePasswordEncryption(parse)
    
    secretPass = IntermediaryUtils.getConfigPrivilegeExecHash(parse)
    if len(secretPass) != 0:
        jsonConfig["enable secret"] = secretPass

    jsonConfig["hostname"] = IntermediaryUtils.getConfigHostname(parse)

    jsonConfig["interfaces"] = IntermediaryUtils.getConfigInterfaces(parse)

    routingProtocols = IntermediaryUtils.getConfigRoutingProtocol(parse)
    if len(routingProtocols) != 0:
        jsonConfig["routing protocol"] = routingProtocols

    bannerMOTD = IntermediaryUtils.getConfigBannerMOTD(parse)
    if len(bannerMOTD) != 0:
        jsonConfig["banner motd"] = bannerMOTD

    lineConsole = IntermediaryUtils.getConfigConsolePassword(parse)
    if len(lineConsole) != 0:
        jsonConfig["line console"] = lineConsole

    lineVty = IntermediaryUtils.getConfigLineVTY(parse)
    if len(lineVty) != 0:
        jsonConfig["line vty"] = lineVty

    ipDefaultGateWay = IntermediaryUtils.getConfigIPDefaultGateway(parse)
    if ipDefaultGateWay:
        jsonConfig["default gateway"] = ipDefaultGateWay

    localUserAccount = IntermediaryUtils.getLocalUserAccount(parse)
    if localUserAccount:
        jsonConfig["local user account"] = localUserAccount

    ipDomainLookup = IntermediaryUtils.getIPDomainLookup(parse)
    jsonConfig["ip domain-name lookup"] = ipDomainLookup

    ipDomainName = IntermediaryUtils.getIPDomainName(parse)
    if len(ipDomainName) != 0:
        jsonConfig["ip domain-name"] = ipDomainName

    dhcp = IntermediaryUtils.getDHCP(parse)
    if len(dhcp) != 0:
        jsonConfig["dhcp"] = dhcp

    acl = IntermediaryUtils.getConfigACL(parse)
    if len(acl) != 0:
        jsonConfig["acl"] = acl

    nat = IntermediaryUtils.getConfigNAT(parse)
    if len(nat) != 0:
        jsonConfig["nat"] = nat

    staticRoutes = IntermediaryUtils.getStaticRoutes(parse)
    if len(staticRoutes) != 0:
        jsonConfig["static routes"] = staticRoutes

    vlan = IntermediaryUtils.getConfigVlan(parse)
    if len(vlan) != 0:
        jsonConfig["vlan"] = vlan

    return jsonConfig

    # ToDO!!
    # Extract NAT configurations (if present) # Implemented but not Tested

    # Extract static route configurations (if present) # Implemented but not Tested

    # Extract VLAN configurations (if present) # Implemented but not Tested

    return jsonConfig


