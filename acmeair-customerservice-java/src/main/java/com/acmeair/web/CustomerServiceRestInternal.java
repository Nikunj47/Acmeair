/*******************************************************************************
 * Copyright (c) 2013 IBM Corp.
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

package com.acmeair.web;

import java.io.StringReader;
import java.util.logging.Level;
import java.util.logging.Logger;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.json.Json;
import jakarta.json.JsonObject;
import jakarta.json.JsonReader;
import jakarta.json.JsonReaderFactory;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.FormParam;

import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;

import org.eclipse.microprofile.metrics.annotation.Timed;

import com.acmeair.service.CustomerService;

import com.acmeair.web.dto.AddressInfo;
import com.acmeair.web.dto.CustomerInfo;



@Path("/internal")
@ApplicationScoped
public class CustomerServiceRestInternal {

  // This class contains endpoints that are called by other services.
  // In the real world, these should be secured somehow, but for simplicity and to avoid too much overhead, they are not.
  // the other endpoints generate enough JWT/security work for this benchmark.
  
  @Inject
  CustomerService customerService;
   
  private static final Logger logger = Logger.getLogger(CustomerServiceRestInternal.class.getName());
  private static final JsonReaderFactory rfactory = Json.createReaderFactory(null);
  
  /**
   * Validate user/password.
   */
  @POST
  @Path("/validateid")
  @Consumes({ "application/x-www-form-urlencoded" })
  @Produces("application/json")
  @Timed(name="com.acmeair.web.CustomerServiceRestInternal.validateCustomer", tags= {"app=acmeair-customerservice-java"})
  public LoginResponse validateCustomer( 
      @FormParam("login") String login,
      @FormParam("password") String password) {

    if (logger.isLoggable(Level.FINE)) {
      logger.fine("validateid : login " + login + " password " + password);
    }
    
    if (!customerService.isPopulated()) {
      throw new RuntimeException("Customer DB has not been populated");
    }

    Boolean validCustomer = customerService.validateCustomer(login, password);

    return new LoginResponse(validCustomer); 
  }

  /**
   * Update reward miles.
   */
  @POST
  @Path("/updateCustomerTotalMiles/{custid}")
  @Consumes({ "application/x-www-form-urlencoded" })
  @Produces("application/json")
  @Timed(name="com.acmeair.web.CustomerServiceRestInternal.updateCustomerTotalMiles", tags={"app=acmeair-customerservice-java"})
  public MilesResponse updateCustomerTotalMiles(
      @PathParam("custid") String customerid,
      @FormParam("miles") Long miles) {
    
    JsonReader jsonReader = rfactory.createReader(new StringReader(customerService
        .getCustomerByUsername(customerid)));

    JsonObject customerJson = jsonReader.readObject();
    jsonReader.close();

    JsonObject addressJson = customerJson.getJsonObject("address");

    String streetAddress2 = null;

    if (addressJson.get("streetAddress2") != null 
        && !addressJson.get("streetAddress2").toString().equals("null")) {
      streetAddress2 = addressJson.getString("streetAddress2");
    }

    AddressInfo addressInfo = new AddressInfo(addressJson.getString("streetAddress1"), 
        streetAddress2,
        addressJson.getString("city"), 
        addressJson.getString("stateProvince"),
        addressJson.getString("country"),
        addressJson.getString("postalCode"));

    Long milesUpdate = customerJson.getInt("total_miles") + miles;
    CustomerInfo customerInfo = new CustomerInfo(customerid, 
        null, 
        customerJson.getString("status"),
        milesUpdate.intValue(), 
        customerJson.getInt("miles_ytd"), 
        addressInfo, 
        customerJson.getString("phoneNumber"),
        customerJson.getString("phoneNumberType"));

    customerService.updateCustomer(customerid, customerInfo);

    return new MilesResponse(milesUpdate);
  }
}
