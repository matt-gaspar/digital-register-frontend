def process_titles(data_directory)
  #TODO: this path should be modified once we know what our acceptance environments will be like
  ENV["REGISTER_FILES_PATH"] = "/vagrant/apps/digital-register-feeder/acceptance-tests-data/#{data_directory}"
  result = `sh consume_register_entries.sh`
  puts result
  if $?.to_i == 0
    puts "Error creating title"
  end
end

def insert_property_non_private_individual_owner
  process_titles("non-private-individual-owner")
  {
    :title_number => "AGL1000",
    :last_changed => "02 July 1996 at 00:59:59",
    :owners => ["HEATHER POOLE PLC"],
    :postcode => "PL9 7FN",
    :town => "Plymouth",
    :house_number => 21,
    :street_name => "Murhill Lane"
  }
end

def insert_property_private_individual_owner
  process_titles("private-individual-owner")
  {
    :title_number => "AGL1001"
  }
end

def insert_property_charity_non_private_individual_owner
  process_titles("charity-non-private-individual-owner")
  {
    :title_number => "AGL1003",
    :last_changed => "28 August 2003 at 14:45:50",
    :owners => ["HEATHER JONES","JOHN JONES","HEATHER SMITH"],
    :postcode => "PL9 7FN",
    :town => "Plymouth",
    :house_number => 21,
    :street_name => "Murhill Lane"
  }
end

def insert_property_charity_private_individual_owner
  process_titles("charity-private-individual-owner")
  {
    :title_number => "AGL1002"
  }
end
