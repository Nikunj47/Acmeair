#!/bin/bash
# Copyright (c) 2018 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

MANIFESTS=manifests-openshift
DOCKERFILE=Dockerfile

EXTERNAL_REGISTRY=$(oc get route default-route -n openshift-image-registry --template='{{ .spec.host }}')
PROJECT_NAME=$(oc project -q)


if [[ ${1} == "" ]]
then
  echo "Using Docker to build/push"
  BUILD_TOOL="docker"
else
  echo "Using podman to build/push"
  BUILD_TOOL="podman"
  TLS_VERIFY="--tls-verify=false"
fi

echo "Trying ${BUILD_TOOL} login -u $(oc whoami) -p $(oc whoami -t) ${TLS_VERIFY}  ${EXTERNAL_REGISTRY}"
echo Loki_%47 | sudo -S ${BUILD_TOOL} login -u $(oc whoami) -p $(oc whoami -t) ${TLS_VERIFY}  ${EXTERNAL_REGISTRY}

if [[ $? -ne 0 ]]
then
  echo "Login Failed" 
  exit
fi

kubectl create secret docker-registry regcred --docker-server=$EXTERNAL_REGISTRY --docker-username=$(oc whoami) --docker-password=$(oc whoami -t)

MONGO_CLONE=$EXTERNAL_REGISTRY/$PROJECT_NAME/mongo
docker pull mongo
docker tag mongo $MONGO_CLONE
docker push $MONGO_CLONE

sed -i "s|image: mongo|image: ${MONGO_CLONE}|" ../acmeair-flightservice-java/manifests-openshift/deploy-acmeair-flightservice-java.yaml
sed -i "s|image: mongo|image: ${MONGO_CLONE}|" ../acmeair-customerservice-java/manifests-openshift/deploy-acmeair-customerservice-java.yaml
sed -i "s|image: mongo|image: ${MONGO_CLONE}|" ../acmeair-bookingservice-java/manifests-openshift/deploy-acmeair-bookingservice-java.yaml


IMAGE_PREFIX_EXTERNAL=${EXTERNAL_REGISTRY}/${PROJECT_NAME}
IMAGE_PREFIX=image-registry.openshift-image-registry.svc:5000/${PROJECT_NAME}
ROUTE_HOST=$PROJECT_NAME$(echo $EXTERNAL_REGISTRY | awk '{gsub("default-route-openshift-image-registry","");print $1}')

echo "Image Prefix External=${IMAGE_PREFIX_EXTERNAL}"
echo "Image Prefix Internal=${IMAGE_PREFIX}"
echo "Route Host=${ROUTE_HOST}"

cd "$(dirname "$0")"
cd ..
kubectl delete -f ${MANIFESTS}
mvn clean package
echo Loki_%47 | sudo -S ${BUILD_TOOL} build --pull -t ${IMAGE_PREFIX_EXTERNAL}/acmeair-mainservice-java:latest --no-cache -f ${DOCKERFILE} .
echo Loki_%47 | sudo -S ${BUILD_TOOL} push ${IMAGE_PREFIX_EXTERNAL}/acmeair-mainservice-java:latest ${TLS_VERIFY}

if [[ `grep -c ${IMAGE_PREFIX} ${MANIFESTS}/deploy-acmeair-mainservice-java.yaml` == 0 ]]
then
  echo "Adding ${IMAGE_PREFIX}/"
  sed -i.bak "s@acmeair-mainservice-java:latest@${IMAGE_PREFIX}/acmeair-mainservice-java:latest@" ${MANIFESTS}/deploy-acmeair-mainservice-java.yaml
fi

if [[ `grep -c ${ROUTE_HOST} ${MANIFESTS}/acmeair-mainservice-route.yaml` == 0 ]]
then
  echo "Patching Route Host: ${ROUTE_HOST}"
  sed -i.bak "s@_HOST_@${ROUTE_HOST}@" ${MANIFESTS}/acmeair-mainservice-route.yaml
fi

kubectl apply -f ${MANIFESTS}

echo "Removing ${IMAGE_PREFIX}"
sed -i.bak "s@${IMAGE_PREFIX}/acmeair-mainservice-java:latest@acmeair-mainservice-java:latest@" ${MANIFESTS}/deploy-acmeair-mainservice-java.yaml

echo "Removing ${ROUTE_HOST}"
sed -i.bak "s@${ROUTE_HOST}@_HOST_@" ${MANIFESTS}/acmeair-mainservice-route.yaml

rm ${MANIFESTS}/acmeair-mainservice-route.yaml.bak
rm ${MANIFESTS}/deploy-acmeair-mainservice-java.yaml.bak

cd ../acmeair-authservice-java
kubectl delete -f ${MANIFESTS}
mvn clean package
echo Loki_%47 | sudo -S ${BUILD_TOOL} build --pull -t ${IMAGE_PREFIX_EXTERNAL}/acmeair-authservice-java --no-cache -f ${DOCKERFILE} .
echo Loki_%47 | sudo -S ${BUILD_TOOL} push ${IMAGE_PREFIX_EXTERNAL}/acmeair-authservice-java:latest ${TLS_VERIFY} 

if [[ `grep -c ${IMAGE_PREFIX} ${MANIFESTS}/deploy-acmeair-authservice-java.yaml` == 0 ]]
then
  echo "Adding ${IMAGE_PREFIX}/"
  sed -i.bak "s@acmeair-authservice-java:latest@${IMAGE_PREFIX}/acmeair-authservice-java:latest@" ${MANIFESTS}/deploy-acmeair-authservice-java.yaml
fi

if [[ `grep -c ${ROUTE_HOST} ${MANIFESTS}/acmeair-authservice-route.yaml` == 0 ]]
then
  echo "Patching Route Host: ${ROUTE_HOST}"
  sed -i.bak "s@_HOST_@${ROUTE_HOST}@" ${MANIFESTS}/acmeair-authservice-route.yaml
fi

kubectl apply -f ${MANIFESTS}

echo "Removing ${IMAGE_PREFIX}"
sed -i.bak "s@${IMAGE_PREFIX}/acmeair-authservice-java:latest@acmeair-authservice-java:latest@" ${MANIFESTS}/deploy-acmeair-authservice-java.yaml

echo "Removing ${ROUTE_HOST}"
sed -i.bak "s@${ROUTE_HOST}@_HOST_@" ${MANIFESTS}/acmeair-authservice-route.yaml

rm ${MANIFESTS}/acmeair-authservice-route.yaml.bak
rm ${MANIFESTS}/deploy-acmeair-authservice-java.yaml.bak

cd ../acmeair-bookingservice-java
kubectl delete -f ${MANIFESTS}
mvn clean package
echo Loki_%47 | sudo -S ${BUILD_TOOL} build --pull -t ${IMAGE_PREFIX_EXTERNAL}/acmeair-bookingservice-java --no-cache -f ${DOCKERFILE} .
echo Loki_%47 | sudo -S ${BUILD_TOOL} push ${IMAGE_PREFIX_EXTERNAL}/acmeair-bookingservice-java:latest ${TLS_VERIFY} 

if [[ `grep -c ${IMAGE_PREFIX}/a ${MANIFESTS}/deploy-acmeair-bookingservice-java.yaml` == 0 ]]
then
  echo "Adding ${IMAGE_PREFIX}/"
  sed -i.bak "s@acmeair-bookingservice-java:latest@${IMAGE_PREFIX}/acmeair-bookingservice-java:latest@" ${MANIFESTS}/deploy-acmeair-bookingservice-java.yaml
fi

if [[ `grep -c ${ROUTE_HOST} ${MANIFESTS}/acmeair-bookingservice-route.yaml` == 0 ]]
then
  echo "Patching Route Host: ${ROUTE_HOST}"
  sed -i.bak "s@_HOST_@${ROUTE_HOST}@" ${MANIFESTS}/acmeair-bookingservice-route.yaml
fi

kubectl apply -f ${MANIFESTS}
kubectl patch deployment acmeair-booking-db -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"regcred"}], "containers":[{"name":"acmeair-booking-db","imagePullPolicy":"Always" }]}}}}'

echo "Removing ${IMAGE_PREFIX}"
sed -i.bak "s@${IMAGE_PREFIX}/acmeair-bookingservice-java:latest@acmeair-bookingservice-java:latest@" ${MANIFESTS}/deploy-acmeair-bookingservice-java.yaml

echo "Removing ${ROUTE_HOST}"
sed -i.bak "s@${ROUTE_HOST}@_HOST_@" ${MANIFESTS}/acmeair-bookingservice-route.yaml

rm ${MANIFESTS}/acmeair-bookingservice-route.yaml.bak
rm ${MANIFESTS}/deploy-acmeair-bookingservice-java.yaml.bak



cd ../acmeair-customerservice-java
kubectl delete -f ${MANIFESTS}
mvn clean package
echo Loki_%47 | sudo -S ${BUILD_TOOL} build --pull -t ${IMAGE_PREFIX_EXTERNAL}/acmeair-customerservice-java --no-cache -f ${DOCKERFILE} .
echo Loki_%47 | sudo -S ${BUILD_TOOL} push ${IMAGE_PREFIX_EXTERNAL}/acmeair-customerservice-java:latest ${TLS_VERIFY} 

if [[ `grep -c ${IMAGE_PREFIX}/a ${MANIFESTS}/deploy-acmeair-customerservice-java.yaml` == 0 ]]
then
  echo "Adding ${IMAGE_PREFIX}/"
  sed -i.bak "s@acmeair-customerservice-java:latest@${IMAGE_PREFIX}/acmeair-customerservice-java:latest@" ${MANIFESTS}/deploy-acmeair-customerservice-java.yaml
fi

if [[ `grep -c ${ROUTE_HOST} ${MANIFESTS}/acmeair-customerservice-route.yaml` == 0 ]]
then
  echo "Patching Route Host: ${ROUTE_HOST}"
  sed -i.bak "s@_HOST_@${ROUTE_HOST}@" ${MANIFESTS}/acmeair-customerservice-route.yaml
fi

kubectl apply -f ${MANIFESTS}
kubectl patch deployment acmeair-customer-db -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"regcred"}], "containers":[{"name":"acmeair-customer-db","imagePullPolicy":"Always" }]}}}}'

echo "Removing ${IMAGE_PREFIX}"
sed -i.bak "s@${IMAGE_PREFIX}/acmeair-customerservice-java:latest@acmeair-customerservice-java:latest@" ${MANIFESTS}/deploy-acmeair-customerservice-java.yaml

echo "Removing ${ROUTE_HOST}"
sed -i.bak "s@${ROUTE_HOST}@_HOST_@" ${MANIFESTS}/acmeair-customerservice-route.yaml

rm ${MANIFESTS}/acmeair-customerservice-route.yaml.bak
rm ${MANIFESTS}/deploy-acmeair-customerservice-java.yaml.bak

cd ../acmeair-flightservice-java
kubectl delete -f ${MANIFESTS}
mvn clean package
echo Loki_%47 | sudo -S ${BUILD_TOOL} build --pull -t ${IMAGE_PREFIX_EXTERNAL}/acmeair-flightservice-java --no-cache -f ${DOCKERFILE} .
echo Loki_%47 | sudo -S ${BUILD_TOOL} push ${IMAGE_PREFIX_EXTERNAL}/acmeair-flightservice-java:latest ${TLS_VERIFY}

if [[ `grep -c ${IMAGE_PREFIX}/a ${MANIFESTS}/deploy-acmeair-flightservice-java.yaml` == 0 ]]
then
  echo "Adding ${IMAGE_PREFIX}/"
  sed -i.bak "s@acmeair-flightservice-java:latest@${IMAGE_PREFIX}/acmeair-flightservice-java:latest@" ${MANIFESTS}/deploy-acmeair-flightservice-java.yaml
fi

if [[ `grep -c ${ROUTE_HOST} ${MANIFESTS}/acmeair-flightservice-route.yaml` == 0 ]]
then
  echo "Patching Route Host: ${ROUTE_HOST}"
  sed -i.bak "s@_HOST_@${ROUTE_HOST}@" ${MANIFESTS}/acmeair-flightservice-route.yaml
fi

kubectl apply -f ${MANIFESTS}
kubectl patch deployment acmeair-flight-db -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"regcred"}], "containers":[{"name":"acmeair-flight-db","imagePullPolicy":"Always" }]}}}}'

echo "Removing ${IMAGE_PREFIX}"
sed -i.bak "s@${IMAGE_PREFIX}/acmeair-flightservice-java:latest@acmeair-flightservice-java:latest@" ${MANIFESTS}/deploy-acmeair-flightservice-java.yaml

echo "Removing ${ROUTE_HOST}"
sed -i.bak "s@${ROUTE_HOST}@_HOST_@" ${MANIFESTS}/acmeair-flightservice-route.yaml

rm ${MANIFESTS}/acmeair-flightservice-route.yaml.bak
rm ${MANIFESTS}/deploy-acmeair-flightservice-java.yaml.bak
