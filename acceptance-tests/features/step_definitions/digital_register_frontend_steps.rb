Given(/^I am a citizen$/) do
  #do nothing
end

Given(/^I have logged in$/) do
  #TODO: will need to be addressed as part of US53
end

Given(/^I have a property$/) do
  # empty the database
  delete_all_titles
  # insert the property_hash data into the database
  @property_hash = {
    :title_number => "DN1000",
    :postcode => "PL9 BLT",
    :street_name => "Test Street",
    :house_no => 13,
    :town => "Plymouth"
  }
  create_title_in_db(@property_hash)
end

Given(/^I do not have a property$/) do
  # empty the database
  delete_all_titles
  @property_hash = {
    :title_number => "DN1000"
  }
  #Do not create the title in the database
end

When(/^I view the property detail page$/) do
  visit("http://landregistry.local:8003/titles/#{@property_hash[:title_number]}")
end

Then(/^I see the full address of the property$/) do
  content = page.body.text
  expect(content).to include(@property_hash[:postcode])
  expect(content).to include(@property_hash[:town])
  expect(content).to include("#{@property_hash[:house_no]} #{@property_hash[:street_name]}")
end

Then(/^I see the title number of the property$/) do
  content = page.body.text
  expect(content).to include(@property_hash[:title_number])
end

Then(/^I get a page not found message$/) do
  expect(page.status_code).to eq(404)
end