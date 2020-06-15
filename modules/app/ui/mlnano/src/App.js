import React, { useState, useReducer, useEffect } from 'react'
import { withAuthenticator } from '@aws-amplify/ui-react'
import { Storage, API, graphqlOperation } from 'aws-amplify'
import uuid from 'uuid/v4'
import { createDataSet as CreateDataSet } from './graphql/mutations'
import { listDataSets } from './graphql/queries'
import { onCreateDataSet } from './graphql/subscriptions'
import config from './aws-exports'

const {
  aws_dataSet_files_s3_bucket_region: region,
  aws_dataSet_files_s3_bucket: bucket
} = config

const initialState = {
  dataSets: []
}

function reducer(state, action) {
  switch(action.type) {
    case 'SET_DATASETS':
      return { ...state, dataSets: action.dataSets }
    case 'ADD_DATASET':
      return { ...state, dataSets: [action.dataSet, ...state.dataSets] }
    default:
      return state
  }
}

function App() {
  const [file, updateFile] = useState(null)
  const [dataSetname, updateDataSetname] = useState('')
  const [state, dispatch] = useReducer(reducer, initialState)
  const [updateAvatarUrl] = useState('')

  function handleChange(event) {
    const { target: { value, files } } = event
    const [image] = files || []
    updateFile(image || value)
  }

  async function fetchImage(key) {
    try {
      const imageData = await Storage.get(key)
      updateAvatarUrl(imageData)
    } catch(err) {
      console.log('error: ', err)
    }
  }

  async function fetchDataSets() {
    try {
     let dataSets = await API.graphql(graphqlOperation(listDataSets))
     dataSets = dataSets.data.listDataSets.items
     dispatch({ type: 'SET_DATASETS', dataSets })
    } catch(err) {
      console.log('error fetching dataSets')
    }
  }

  async function createDataSet() {
    if (!dataSetname) return alert('please enter a dataSetname')
    if (file && dataSetname) {
        const { name: fileName, type: mimeType } = file
        const key = `${uuid()}${fileName}`
        const fileForUpload = {
            bucket,
            key,
            region,
        }
        const inputData = { name: dataSetname, file: fileForUpload }

        try {
          await Storage.put(key, file, {
            level: 'private',
            contentType: mimeType
          })
          console.log(inputData)
          await API.graphql(graphqlOperation(CreateDataSet, { input: inputData }))
          updateDataSetname('')
          console.log('successfully stored dataSet data!')
        } catch (err) {
          console.log('error: ', err)
        }
    }
  }
  useEffect(() => {
    fetchDataSets()
    const subscription = API.graphql(graphqlOperation(onCreateDataSet))
      .subscribe({
        next: async dataSetData => {
          const { onCreateDataSet } = dataSetData.value.data
          dispatch({ type: 'ADD_DATASET', dataSet: onCreateDataSet })
        }
      })
    return () => subscription.unsubscribe()
  }, [])

  return (
    <div style={styles.container}>
      <input
        label="File to upload"
        type="file"
        onChange={handleChange}
        style={{margin: '10px 0px'}}
      />
      <input
        placeholder='DataSetname'
        value={dataSetname}
        onChange={e => updateDataSetname(e.target.value)}
      />
      <button
        style={styles.button}
        onClick={createDataSet}>Save Data Set</button>
      {
        state.dataSets.map((u, i) => {
          return (
            <div
              key={i}
            >
              <p
                style={styles.dataSetname}
               onClick={() => fetchImage(u.file.key)}>{u.dataSetname}</p>
            </div>
          )
        })
      }
    </div>
  )
}

const styles = {
  container: {
    width: 300,
    margin: '0 auto'
  },
  dataSetname: {
    cursor: 'pointer',
    border: '1px solid #ddd',
    padding: '5px 25px'
  },
  button: {
    width: 200,
    backgroundColor: '#ddd',
    cursor: 'pointer',
    height: 30,
    margin: '0px 0px 8px'
  }
}

export default withAuthenticator(App, { includeGreetings: true })
