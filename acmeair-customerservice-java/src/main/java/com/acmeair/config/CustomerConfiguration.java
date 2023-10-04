/*******************************************************************************
* Copyright (c) 2017 IBM Corp.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/

package com.acmeair.config;

import com.acmeair.service.CustomerService;

import java.util.logging.Logger;

import jakarta.inject.Inject;
import jakarta.json.Json;
import jakarta.json.JsonArray;
import jakarta.json.JsonBuilderFactory;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.Response;

@Path("/config")
public class CustomerConfiguration {
    
  Logger logger = Logger.getLogger(CustomerConfiguration.class.getName());

  @Inject
  CustomerService customerService;

  public CustomerConfiguration() {
    super();
  }
  
  /**
   * Return count of customer from the db.
   */
  @GET
  @Path("/countCustomers")
  @Produces("application/json")
  public Response countCustomer() {
    try {
      String customerCount = customerService.count().toString();
      
      return Response.ok(customerCount).build();
    } catch (Exception e) {
      e.printStackTrace();
      return Response.ok(-1).build();
    }
  }
  
  /**
   * Return active db impl.
   */
  @GET
  @Path("/activeDataService")
  @Produces("application/json")
  public Response getActiveDataServiceInfo() {
    try {
      logger.fine("Get active Data Service info");
      return  Response.ok(customerService.getServiceType()).build();
    } catch (Exception e) {
      e.printStackTrace();
      return Response.ok("Unknown").build();
    }
  }
  
  /**
   * Return runtim info.
   */
  @GET
  @Path("/runtime")
  @Produces("application/json")
  public String getRuntimeInfo() {
    JsonBuilderFactory factory = Json.createBuilderFactory(null);
    JsonArray value = factory.createArrayBuilder()
        .add(factory.createObjectBuilder()
            .add("name", "Runtime")
            .add("description", "Java"))
        .add(factory.createObjectBuilder()
            .add("name", "Version")
            .add("description", System.getProperty("java.version")))
        .add(factory.createObjectBuilder()
            .add("name", "Vendor")
            .add("description", System.getProperty("java.vendor")))
        .build();
    
    return value.toString();
  }
}
