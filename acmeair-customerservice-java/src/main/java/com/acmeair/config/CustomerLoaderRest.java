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

import com.acmeair.loader.CustomerLoader;

import jakarta.inject.Inject;
import jakarta.ws.rs.DefaultValue;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.Response;

@Path("/loader")
public class CustomerLoaderRest {

  @Inject
  private CustomerLoader loader;
  
  @GET
  @Path("/query")
  @Produces("text/plain")
  public Response queryLoader() {
    String response = loader.queryLoader();
    return Response.ok(response).build();
  }
  
  
  @GET
  @Path("/load")
  @Produces("text/plain")
  public Response loadDb(@DefaultValue("-1") @QueryParam("numCustomers") long numCustomers) {
    String response = loader.loadCustomerDb(numCustomers);
    return Response.ok(response).build();
  }
}
