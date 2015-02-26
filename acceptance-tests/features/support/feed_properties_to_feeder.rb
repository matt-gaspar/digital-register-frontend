def process_titles(data_directory)
  ENV["REGISTER_FILES_PATH"] = "/vagrant/apps/digital-register-feeder/acceptance-tests-data/#{data_directory}"
  result = `sh consume_register_entries.sh`
  puts result
  unless $?.to_i == 0
    raise "Error creating title"
  end
end

def insert_property_non_private_individual_owner
  process_titles("non-private-individual-owner")
  "AGL1000"
end

def insert_property_private_individual_owner
  process_titles("private-individual-owner")
  "AGL1001"
end

def insert_property_charity_non_private_individual_owner
  process_titles("charity-non-private-individual-owner")
  "AGL1003"
end

def insert_property_charity_private_individual_owner
  process_titles("charity-private-individual-owner")
  "AGL1002"
end
